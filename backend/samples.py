"""
Supported languages and sample code snippets for LegacyLens.
"""
import textwrap

# ─────────────────────────────────────────────────────────────────────────────
# Supported Languages
# ─────────────────────────────────────────────────────────────────────────────
SUPPORTED_LANGUAGES: list[str] = [
    "RPGLE / AS400",
    "COBOL",
    "JCL",
    "PL/I",
    "Natural / ADABAS",
    "CL (Control Language)",
]

# ─────────────────────────────────────────────────────────────────────────────
# Sample Code Snippets
# ─────────────────────────────────────────────────────────────────────────────
SAMPLE_RPGLE_CODE: str = textwrap.dedent("""\
    **FREE
    // ================================================================
    // Program  : CUSTUPD
    // Purpose  : Update customer billing address and flag arrears
    // Author   : J. Smith
    // Date     : 2003-05-14
    // ================================================================

    DCL-F CUSTMAST DISK(*UPDATE) KEYED;
    DCL-F ARREARSF DISK(*UPDATE) KEYED;
    DCL-F AUDITLOG DISK(*ADD);

    DCL-S wkCustNo   CHAR(10);
    DCL-S wkNewAddr  CHAR(60);
    DCL-S wkNewCity  CHAR(30);
    DCL-S wkNewState CHAR(2);
    DCL-S wkNewZip   CHAR(10);
    DCL-S wkBalance  PACKED(11:2);
    DCL-S wkArFlag   CHAR(1);
    DCL-S wkLogDate  DATE(*ISO);
    DCL-S wkLogTime  TIME(*ISO);
    DCL-S wkLogMsg   CHAR(100);

    DCL-C ARREARS_THRESHOLD 5000.00;

    // ── Main Processing ──────────────────────────────────────────
    EXSR $GetInput;

    CHAIN wkCustNo CUSTMAST;
    IF %FOUND(CUSTMAST);
       // Update billing address fields
       CUADDR = wkNewAddr;
       CUCITY = wkNewCity;
       CUSTAT = wkNewState;
       CUZIP  = wkNewZip;
       UPDATE CUSTREC;

       // Check outstanding balance for arrears flagging
       CHAIN wkCustNo ARREARSF;
       IF %FOUND(ARREARSF);
          wkBalance = ARBAL;
          IF wkBalance > ARREARS_THRESHOLD;
             wkArFlag = 'Y';
             ARFLAG = wkArFlag;
             UPDATE ARRECSF;

             // Write to audit log
             wkLogDate = %DATE();
             wkLogTime = %TIME();
             wkLogMsg = 'Arrears flag set for customer ' + wkCustNo;
             LGDATE = wkLogDate;
             LGTIME = wkLogTime;
             LGMSG  = wkLogMsg;
             LGCUST = wkCustNo;
             WRITE AUDITRC;
          ENDIF;
       ENDIF;

       DSPLY ('Customer ' + %TRIMR(wkCustNo) + ' updated.');
    ELSE;
       DSPLY ('Customer ' + %TRIMR(wkCustNo) + ' NOT found.');
    ENDIF;

    *INLR = *ON;
    RETURN;

    // ── Subroutine: Read input parameters ────────────────────────
    BEGSR $GetInput;
       wkCustNo   = 'CUST001234';
       wkNewAddr  = '742 Evergreen Terrace';
       wkNewCity  = 'Springfield';
       wkNewState = 'IL';
       wkNewZip   = '62704';
    ENDSR;
""")

SAMPLE_COBOL_CODE: str = textwrap.dedent("""\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CUSTBAL.
       AUTHOR.     J. SMITH.
      *================================================================
      * Purpose: Read customer master file, compute monthly interest
      *          on outstanding balances, and write a summary report.
      *================================================================

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT CUST-FILE ASSIGN TO 'CUSTMAST'
               ORGANIZATION IS INDEXED
               ACCESS MODE IS SEQUENTIAL
               RECORD KEY IS CUST-ID
               FILE STATUS IS WS-FILE-STATUS.
           SELECT REPORT-FILE ASSIGN TO 'CUSTRPT'
               ORGANIZATION IS LINE SEQUENTIAL.

       DATA DIVISION.
       FILE SECTION.
       FD  CUST-FILE.
       01  CUST-RECORD.
           05  CUST-ID          PIC X(10).
           05  CUST-NAME        PIC X(30).
           05  CUST-BALANCE     PIC S9(9)V99.
           05  CUST-RATE        PIC 9V9(4).
           05  CUST-STATUS      PIC X(1).

       FD  REPORT-FILE.
       01  REPORT-LINE          PIC X(132).

       WORKING-STORAGE SECTION.
       01  WS-FILE-STATUS       PIC XX.
       01  WS-EOF               PIC X VALUE 'N'.
       01  WS-INTEREST          PIC S9(9)V99.
       01  WS-NEW-BALANCE       PIC S9(9)V99.
       01  WS-TOTAL-INTEREST    PIC S9(11)V99 VALUE ZEROS.
       01  WS-RECORD-COUNT      PIC 9(6) VALUE ZEROS.

       PROCEDURE DIVISION.
       0000-MAIN.
           OPEN INPUT CUST-FILE
                OUTPUT REPORT-FILE
           PERFORM 1000-READ-CUSTOMER
           PERFORM 2000-PROCESS-CUSTOMER
               UNTIL WS-EOF = 'Y'
           PERFORM 3000-WRITE-TOTALS
           CLOSE CUST-FILE REPORT-FILE
           STOP RUN.

       1000-READ-CUSTOMER.
           READ CUST-FILE
               AT END MOVE 'Y' TO WS-EOF
           END-READ.

       2000-PROCESS-CUSTOMER.
           IF CUST-STATUS = 'A'
               COMPUTE WS-INTEREST =
                   CUST-BALANCE * CUST-RATE / 12
               COMPUTE WS-NEW-BALANCE =
                   CUST-BALANCE + WS-INTEREST
               ADD WS-INTEREST TO WS-TOTAL-INTEREST
               ADD 1 TO WS-RECORD-COUNT
               MOVE WS-NEW-BALANCE TO CUST-BALANCE
               REWRITE CUST-RECORD
           END-IF
           PERFORM 1000-READ-CUSTOMER.

       3000-WRITE-TOTALS.
           STRING 'Total Records: ' WS-RECORD-COUNT
                  '  Total Interest: ' WS-TOTAL-INTEREST
               DELIMITED BY SIZE INTO REPORT-LINE
           WRITE REPORT-LINE.
""")

SAMPLE_JCL_CODE: str = textwrap.dedent("""\
    //CUSTJOB  JOB  (ACCT),'MONTHLY BILLING',CLASS=A,
    //             MSGCLASS=X,NOTIFY=&SYSUID
    //*================================================================
    //* JOB: Run monthly customer billing cycle
    //*      Step 1: Sort customer records by region
    //*      Step 2: Execute billing COBOL program
    //*      Step 3: Generate PDF report
    //*================================================================
    //STEP01   EXEC PGM=SORT
    //SORTIN   DD   DSN=PROD.CUST.MASTER,DISP=SHR
    //SORTOUT  DD   DSN=PROD.CUST.SORTED,DISP=(NEW,CATLG,DELETE),
    //             SPACE=(CYL,(10,5)),DCB=(RECFM=FB,LRECL=200)
    //SYSIN    DD   *
      SORT FIELDS=(1,10,CH,A,11,2,CH,A)
      INCLUDE COND=(50,1,CH,EQ,C'A')
    /*
    //STEP02   EXEC PGM=CUSTBILL
    //STEPLIB  DD   DSN=PROD.LOADLIB,DISP=SHR
    //CUSTIN   DD   DSN=PROD.CUST.SORTED,DISP=SHR
    //BILLOUT  DD   DSN=PROD.BILLING.OUTPUT,DISP=(NEW,CATLG,DELETE),
    //             SPACE=(CYL,(20,10)),DCB=(RECFM=FB,LRECL=300)
    //SYSPRINT DD   SYSOUT=*
    //STEP03   EXEC PGM=RPTGEN
    //BILLIN   DD   DSN=PROD.BILLING.OUTPUT,DISP=SHR
    //PDFOUT   DD   DSN=PROD.BILLING.REPORT.PDF,DISP=(NEW,CATLG,DELETE),
    //             SPACE=(CYL,(5,2))
    //SYSPRINT DD   SYSOUT=*
""")

SAMPLE_PLI_CODE: str = textwrap.dedent("""\
    CALC_PREMIUM: PROCEDURE OPTIONS(MAIN);
    /*================================================================*/
    /* Program : CALC_PREMIUM                                          */
    /* Purpose : Calculate insurance premium based on risk factors      */
    /*================================================================*/

    DCL POLICY_FILE    FILE RECORD INPUT;
    DCL PREMIUM_FILE   FILE RECORD OUTPUT;

    DCL 1 POLICY_REC,
          2 POLICY_NO      CHAR(12),
          2 HOLDER_NAME    CHAR(40),
          2 AGE            FIXED BIN(15),
          2 RISK_CLASS     CHAR(1),
          2 BASE_PREMIUM   FIXED DEC(9,2),
          2 CLAIM_COUNT    FIXED BIN(15);

    DCL WS_FACTOR       FIXED DEC(5,3);
    DCL WS_FINAL_PREM   FIXED DEC(9,2);
    DCL WS_EOF          BIT(1) INIT('0'B);

    ON ENDFILE(POLICY_FILE) WS_EOF = '1'B;

    OPEN FILE(POLICY_FILE), FILE(PREMIUM_FILE);

    READ FILE(POLICY_FILE) INTO(POLICY_REC);
    DO WHILE(^WS_EOF);
        SELECT(RISK_CLASS);
            WHEN('A') WS_FACTOR = 1.000;
            WHEN('B') WS_FACTOR = 1.250;
            WHEN('C') WS_FACTOR = 1.500;
            WHEN('D') WS_FACTOR = 2.000;
            OTHERWISE WS_FACTOR = 2.500;
        END;

        IF CLAIM_COUNT > 3 THEN
            WS_FACTOR = WS_FACTOR * 1.30;

        IF AGE > 65 THEN
            WS_FACTOR = WS_FACTOR * 1.15;

        WS_FINAL_PREM = BASE_PREMIUM * WS_FACTOR;
        WRITE FILE(PREMIUM_FILE) FROM(POLICY_REC);
        READ FILE(POLICY_FILE) INTO(POLICY_REC);
    END;

    CLOSE FILE(POLICY_FILE), FILE(PREMIUM_FILE);
    END CALC_PREMIUM;
""")

SAMPLE_NATURAL_CODE: str = textwrap.dedent("""\
    * ================================================================
    * Program  : EMPUPD
    * Purpose  : Update employee salary based on department budget
    * Database : ADABAS - Employee file (FNR 150)
    * ================================================================
    DEFINE DATA
    LOCAL
      1 EMPLOYEE-VIEW VIEW OF EMPLOYEES
        2 PERSONNEL-ID   (A8)
        2 NAME           (A30)
        2 DEPARTMENT     (A6)
        2 SALARY         (P9.2)
        2 LAST-REVIEW    (D)
      1 #INCREASE-PCT    (P3.2)
      1 #NEW-SALARY      (P9.2)
      1 #DEPT-BUDGET     (P11.2)
      1 #RECORDS-UPDATED (N5)
    END-DEFINE
    *
    MOVE 5.50 TO #INCREASE-PCT
    RESET #RECORDS-UPDATED
    *
    READ EMPLOYEE-VIEW BY DEPARTMENT
      IF DEPARTMENT = 'ENG001'
        COMPUTE #NEW-SALARY = SALARY * (1 + #INCREASE-PCT / 100)
        IF #NEW-SALARY <= #DEPT-BUDGET
          MOVE #NEW-SALARY TO SALARY
          UPDATE
          ADD 1 TO #RECORDS-UPDATED
        END-IF
      END-IF
    END-READ
    *
    WRITE 'Records updated:' #RECORDS-UPDATED
    END
""")

SAMPLE_CL_CODE: str = textwrap.dedent("""\
    PGM
    /* ================================================================ */
    /* Program  : NIGHTBATCH                                             */
    /* Purpose  : Nightly batch processing - backup, run reports,        */
    /*            clear work files, and send completion notification      */
    /* ================================================================ */

    DCL VAR(&CURDATE)  TYPE(*CHAR) LEN(8)
    DCL VAR(&CURTIME)  TYPE(*CHAR) LEN(6)
    DCL VAR(&JOBSTS)   TYPE(*CHAR) LEN(10) VALUE('SUCCESS')
    DCL VAR(&BKPLIB)   TYPE(*CHAR) LEN(10) VALUE('NIGHTBKP')
    DCL VAR(&MSGTEXT)  TYPE(*CHAR) LEN(256)

    /* Retrieve current date and time */
    RTVSYSVAL  SYSVAL(QDATE) RTNVAR(&CURDATE)
    RTVSYSVAL  SYSVAL(QTIME) RTNVAR(&CURTIME)

    /* Step 1: Save production library */
    MONMSG MSGID(CPF0000) EXEC(DO)
        CHGVAR VAR(&JOBSTS) VALUE('FAILED')
        GOTO CMDLBL(NOTIFY)
    ENDDO
    SAVLIB LIB(PRODLIB) DEV(*SAVF) SAVF(&BKPLIB/PRODBKP)

    /* Step 2: Submit report generation jobs */
    SBMJOB CMD(CALL PGM(RPTMONTH)) JOB(MONTHRPT)
    SBMJOB CMD(CALL PGM(RPTYEAR))  JOB(YEARRPT)

    /* Step 3: Clear work files */
    CLRPFM FILE(WORKLIB/TEMPDATA)
    CLRPFM FILE(WORKLIB/SORTWORK)

    NOTIFY:
    /* Step 4: Send completion message */
    CHGVAR VAR(&MSGTEXT) VALUE('Nightly batch ' *CAT &JOBSTS +
               *BCAT 'at' *BCAT &CURTIME *BCAT 'on' *BCAT &CURDATE)
    SNDMSG MSG(&MSGTEXT) TOUSR(OPSADMIN)

    ENDPGM
""")

# Map language names to their sample code snippets
SAMPLE_CODES: dict[str, str] = {
    "RPGLE / AS400": SAMPLE_RPGLE_CODE,
    "COBOL": SAMPLE_COBOL_CODE,
    "JCL": SAMPLE_JCL_CODE,
    "PL/I": SAMPLE_PLI_CODE,
    "Natural / ADABAS": SAMPLE_NATURAL_CODE,
    "CL (Control Language)": SAMPLE_CL_CODE,
}
