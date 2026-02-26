"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  LegacyLens: Legacy Code Explainer & Modernizer                             ║
║  ─────────────────────────────────────────────                               ║
║  A polished Streamlit application that takes legacy mainframe code           ║
║  (RPGLE, COBOL, JCL, PL/I, Natural/ADABAS, CL) and translates it into      ║
║  human-readable documentation and modern Python equivalents using            ║
║  Google Gemini or Azure OpenAI.                                              ║
║                                                                              ║
║  Author : LegacyLens Team                                                    ║
║  Version: 1.1.0                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ─────────────────────────────────────────────────────────────────────────────
# Imports
# ─────────────────────────────────────────────────────────────────────────────
import streamlit as st
import textwrap
import re
import time
from datetime import datetime

# LLM SDKs — imported lazily inside call functions to keep startup fast,
# but we import them at the top so IDE tooling works.
try:
    import google.generativeai as genai
except ImportError:
    genai = None  # Gemini SDK not installed; user will see a friendly error

try:
    from openai import AzureOpenAI
except ImportError:
    AzureOpenAI = None  # Azure OpenAI SDK not installed


# ─────────────────────────────────────────────────────────────────────────────
# Page Configuration — MUST be the first Streamlit command
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LegacyLens — Legacy Code Explainer & Modernizer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS — Premium dark-themed SaaS aesthetic
# ─────────────────────────────────────────────────────────────────────────────
def inject_custom_css() -> None:
    """Inject custom CSS to give the app a polished, premium SaaS look."""
    st.markdown(
        """
        <style>
        /* ── Import Google Font ────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        /* ── Root Variables ────────────────────────────────────────── */
        :root {
            --ll-primary: #6C63FF;
            --ll-primary-light: #8B83FF;
            --ll-primary-dark: #4F46E5;
            --ll-accent: #00D4AA;
            --ll-accent-light: #34E0BF;
            --ll-bg-dark: #0F1117;
            --ll-bg-card: #1A1D2E;
            --ll-bg-card-hover: #22263A;
            --ll-text-primary: #E8E8ED;
            --ll-text-secondary: #9CA3AF;
            --ll-border: #2D3148;
            --ll-success: #10B981;
            --ll-warning: #F59E0B;
            --ll-error: #EF4444;
            --ll-gradient: linear-gradient(135deg, #6C63FF 0%, #00D4AA 100%);
        }

        /* ── Global Font ───────────────────────────────────────────── */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* ── Hero Header ───────────────────────────────────────────── */
        .hero-header {
            background: linear-gradient(135deg, #1a1d2e 0%, #0f1117 50%, #1a1d2e 100%);
            border: 1px solid var(--ll-border);
            border-radius: 16px;
            padding: 2.5rem 2rem;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
        }
        .hero-header::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: var(--ll-gradient);
        }
        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            background: var(--ll-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
        }
        .hero-subtitle {
            font-size: 1.05rem;
            color: var(--ll-text-secondary);
            font-weight: 400;
            line-height: 1.6;
        }

        /* ── Card Containers ───────────────────────────────────────── */
        .ll-card {
            background: var(--ll-bg-card);
            border: 1px solid var(--ll-border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }
        .ll-card:hover {
            border-color: var(--ll-primary);
            box-shadow: 0 0 20px rgba(108, 99, 255, 0.1);
        }
        .ll-card-title {
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--ll-primary-light);
            margin-bottom: 0.75rem;
        }

        /* ── Sidebar Styling ───────────────────────────────────────── */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #12141F 0%, #0F1117 100%);
            border-right: 1px solid var(--ll-border);
        }
        .sidebar-brand {
            text-align: center;
            padding: 1rem 0 1.5rem;
            border-bottom: 1px solid var(--ll-border);
            margin-bottom: 1.5rem;
        }
        .sidebar-brand-icon {
            font-size: 2.4rem;
            margin-bottom: 0.25rem;
        }
        .sidebar-brand-name {
            font-size: 1.3rem;
            font-weight: 700;
            background: var(--ll-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .sidebar-section-label {
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--ll-text-secondary);
            margin: 1.25rem 0 0.5rem 0;
        }

        /* ── Buttons ───────────────────────────────────────────────── */
        .stButton > button {
            border-radius: 10px;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            transition: all 0.3s ease;
            border: none;
            letter-spacing: 0.01em;
        }
        div[data-testid="stHorizontalBlock"] .stButton > button {
            width: 100%;
            padding: 0.7rem 1.5rem;
        }

        /* ── Tabs ──────────────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            border-bottom: 2px solid var(--ll-border);
        }
        .stTabs [data-baseweb="tab"] {
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            font-family: 'Inter', sans-serif;
            letter-spacing: 0.01em;
        }
        .stTabs [aria-selected="true"] {
            border-bottom: 2px solid var(--ll-primary) !important;
        }

        /* ── Text Area ─────────────────────────────────────────────── */
        .stTextArea textarea {
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace !important;
            font-size: 0.85rem !important;
            line-height: 1.6 !important;
            border-radius: 10px !important;
            border: 1px solid var(--ll-border) !important;
        }
        .stTextArea textarea:focus {
            border-color: var(--ll-primary) !important;
            box-shadow: 0 0 0 2px rgba(108, 99, 255, 0.25) !important;
        }

        /* ── Expanders ─────────────────────────────────────────────── */
        .streamlit-expanderHeader {
            font-weight: 600;
            font-family: 'Inter', sans-serif;
        }

        /* ── Download Button ───────────────────────────────────────── */
        .stDownloadButton > button {
            background: var(--ll-gradient) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
        }
        .stDownloadButton > button:hover {
            opacity: 0.9;
            box-shadow: 0 4px 15px rgba(108, 99, 255, 0.4);
        }

        /* ── Status Badges ─────────────────────────────────────────── */
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.03em;
        }
        .status-ready {
            background: rgba(16, 185, 129, 0.15);
            color: #10B981;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        .status-waiting {
            background: rgba(245, 158, 11, 0.15);
            color: #F59E0B;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        /* ── Footer ────────────────────────────────────────────────── */
        .ll-footer {
            text-align: center;
            padding: 2rem 0 1rem;
            color: var(--ll-text-secondary);
            font-size: 0.8rem;
            border-top: 1px solid var(--ll-border);
            margin-top: 3rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Supported Languages & Sample Code Snippets
# ─────────────────────────────────────────────────────────────────────────────
SUPPORTED_LANGUAGES: list[str] = [
    "RPGLE / AS400",
    "COBOL",
    "JCL",
    "PL/I",
    "Natural / ADABAS",
    "CL (Control Language)",
]

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


# ─────────────────────────────────────────────────────────────────────────────
# Input Validation & Safety Limits
# ─────────────────────────────────────────────────────────────────────────────
# Rough token estimate: 1 token ≈ 4 characters for English/code.
INPUT_WARN_CHARS = 12000   # ~3,000 tokens — show a warning
INPUT_MAX_CHARS = 40000    # ~10,000 tokens — hard block
MAX_RETRIES = 2            # Retry count on rate-limit errors
RETRY_DELAY_SECS = 5       # Wait between retries


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for code."""
    return len(text) // 4


def validate_input(code: str, language: str) -> tuple[bool, str | None]:
    """
    Validate the user's input code before sending to the LLM.

    Returns:
        (is_valid, error_message). If is_valid is True, error_message is None.
    """
    if not code or not code.strip():
        return False, f"⚠️ Please paste some {language} code or load the sample code before running analysis."

    char_count = len(code)
    if char_count > INPUT_MAX_CHARS:
        est_tokens = estimate_tokens(code)
        return False, (
            f"🚫 **Input too large** ({char_count:,} characters, ~{est_tokens:,} tokens).\n\n"
            f"The maximum is {INPUT_MAX_CHARS:,} characters (~{INPUT_MAX_CHARS // 4:,} tokens). "
            f"Please split your code into smaller sections and analyze each part separately."
        )

    return True, None


def check_input_warnings(code: str) -> None:
    """Show non-blocking warnings for large (but allowed) inputs."""
    char_count = len(code)
    if char_count > INPUT_WARN_CHARS:
        est_tokens = estimate_tokens(code)
        st.warning(
            f"⚠️ **Large input** ({char_count:,} chars, ~{est_tokens:,} tokens). "
            f"The output may be truncated if the code is too complex. "
            f"Consider splitting into smaller sections for best results.",
            icon="⚠️",
        )


# ─────────────────────────────────────────────────────────────────────────────
# Prompt Engineering
# ─────────────────────────────────────────────────────────────────────────────
def build_system_prompt(language: str = "RPGLE / AS400") -> str:
    """
    Construct a concise system prompt for the LLM.
    Kept short to minimize token usage on free-tier API keys.
    """
    return textwrap.dedent(f"""\
    You are LegacyLens AI, an expert in legacy mainframe code (RPGLE, COBOL, JCL, PL/I, Natural/ADABAS, CL).
    You are analyzing {language} code.

    Return your response in exactly THREE sections with these markdown headings:

    ## EXECUTIVE SUMMARY
    3-5 sentence plain-English explanation for non-technical stakeholders.

    ## TECHNICAL DOCUMENTATION
    Include: files/tables used, key variables (name, type, purpose), step-by-step logic flow, I/O operations, edge cases.

    ## PYTHON CODE
    Modern Python 3.12+ equivalent with type hints, comments referencing original {language} code, error handling, and a main block.
    """)


def build_user_prompt(legacy_code: str, language: str = "RPGLE / AS400", mode: str = "full") -> str:
    """
    Build the user-facing prompt that wraps the pasted legacy code.

    Args:
        legacy_code: The raw legacy source code from the user.
        language: The legacy language being analyzed.
        mode: "full" for all three sections, "docs_only" for just
              Executive Summary + Technical Documentation,
              "python_only" for just the Python translation.
    """
    mode_instruction = {
        "full": "Provide ALL THREE sections: Executive Summary, Technical Documentation, and Python Code.",
        "docs_only": "Provide ONLY the Executive Summary and Technical Documentation sections. Do NOT include Python Code.",
        "python_only": "Provide ONLY the Python Code section. Do NOT include Executive Summary or Technical Documentation.",
    }
    return textwrap.dedent(f"""\
    Analyze the following **{language}** code.
    {mode_instruction.get(mode, mode_instruction["full"])}

    ```
    {legacy_code}
    ```
    """)


# ─────────────────────────────────────────────────────────────────────────────
# Response Parser — Split LLM output into three sections
# ─────────────────────────────────────────────────────────────────────────────
def parse_llm_response(raw_response: str) -> dict[str, str]:
    """
    Parse the LLM's raw markdown response into three sections by looking
    for the ## headings we instructed it to use.

    Returns a dict with keys: 'executive_summary', 'technical_docs', 'python_code'.
    If a section is missing, its value will be a friendly fallback message.
    """
    sections: dict[str, str] = {
        "executive_summary": "",
        "technical_docs": "",
        "python_code": "",
    }

    # Regex patterns to match section headers (case-insensitive)
    patterns = [
        (r"##\s*EXECUTIVE\s+SUMMARY", "executive_summary"),
        (r"##\s*TECHNICAL\s+DOCUMENTATION", "technical_docs"),
        (r"##\s*PYTHON\s+CODE", "python_code"),
    ]

    # Find start positions for each section
    positions: list[tuple[int, str]] = []
    for pattern, key in patterns:
        match = re.search(pattern, raw_response, re.IGNORECASE)
        if match:
            positions.append((match.start(), key))

    # Sort by position in the text
    positions.sort(key=lambda x: x[0])

    # Extract content between section boundaries
    for i, (start, key) in enumerate(positions):
        # Find the end of the heading line
        heading_end = raw_response.index("\n", start) + 1 if "\n" in raw_response[start:] else len(raw_response)
        # End is either the start of the next section or end of text
        end = positions[i + 1][0] if i + 1 < len(positions) else len(raw_response)
        sections[key] = raw_response[heading_end:end].strip()

    # Friendly fallbacks
    if not sections["executive_summary"]:
        sections["executive_summary"] = "_No executive summary was generated. The LLM may not have followed the expected format._"
    if not sections["technical_docs"]:
        sections["technical_docs"] = "_No technical documentation was generated._"
    if not sections["python_code"]:
        sections["python_code"] = "_No Python code was generated._"

    # Detect truncated output — if the Python section looks incomplete
    python_out = sections["python_code"]
    if python_out and not python_out.startswith("_No"):
        # Only flag truncation if there's an unclosed code block (odd number of ```)
        open_fences = python_out.count("```")
        if open_fences % 2 != 0:
            sections["python_code_truncated"] = True

    return sections


# ─────────────────────────────────────────────────────────────────────────────
# LLM API Callers
# ─────────────────────────────────────────────────────────────────────────────
def call_gemini_api(
    user_prompt: str,
    system_prompt: str,
    api_key: str,
    model_name: str = "gemini-flash-latest",
) -> str:
    """
    Call Google Gemini API using the official SDK.

    Raises:
        RuntimeError: If the SDK is not installed or the API call fails.
    """
    if genai is None:
        raise RuntimeError(
            "The `google-generativeai` package is not installed. "
            "Run `pip install google-generativeai` to fix this."
        )

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_prompt,
    )

    last_error = None
    for attempt in range(1, MAX_RETRIES + 2):  # +2 because range is exclusive and we start at 1
        try:
            response = model.generate_content(
                user_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=8192,
                ),
            )

            # Check for blocked/empty responses
            if not response.text:
                raise RuntimeError(
                    "🚫 **Empty response.** The model returned no output. "
                    "This may happen if the input code was flagged by safety filters. "
                    "Try removing any sensitive data from the code."
                )
            return response.text

        except Exception as e:
            error_msg = str(e).lower()
            last_error = e

            # Auth errors — no retry
            if "api key" in error_msg or "invalid" in error_msg or "authenticate" in error_msg:
                raise RuntimeError(
                    "🔑 **Invalid API Key.** Please check your Gemini API key in the sidebar and try again."
                ) from e

            # Rate limit — retry with backoff
            if "quota" in error_msg or "rate" in error_msg or "429" in error_msg or "resource" in error_msg:
                if attempt <= MAX_RETRIES:
                    wait_time = RETRY_DELAY_SECS * attempt
                    st.toast(f"⏳ Rate limited. Retrying in {wait_time}s... (attempt {attempt}/{MAX_RETRIES})", icon="⏳")
                    time.sleep(wait_time)
                    continue
                else:
                    raise RuntimeError(
                        "⏳ **Rate limit reached** after retries.\n\n"
                        "**What to do:**\n"
                        "- Wait 60 seconds and try again\n"
                        "- Switch to **Gemini Flash (Latest)** in the sidebar for higher limits\n"
                        "- Use **Generate Documentation** instead of **Full Analysis** to reduce output size"
                    ) from e

            # Timeout — retry once
            if "timeout" in error_msg or "deadline" in error_msg:
                if attempt <= MAX_RETRIES:
                    st.toast(f"🕐 Timeout. Retrying... (attempt {attempt}/{MAX_RETRIES})", icon="🕐")
                    time.sleep(2)
                    continue
                else:
                    raise RuntimeError(
                        "🕐 **Request timed out** after retries. The code may be too large. "
                        "Try splitting it into smaller sections."
                    ) from e

            # Safety/content filter
            if "safety" in error_msg or "blocked" in error_msg or "harm" in error_msg:
                raise RuntimeError(
                    "🛡️ **Content blocked by safety filters.** "
                    "The model flagged the input or output. Try removing any "
                    "sensitive data (passwords, PII) from your code snippet."
                ) from e

            # Unknown error — no retry
            raise RuntimeError(f"❌ **Gemini API Error:** {e}") from e

    # Should not reach here, but just in case
    raise RuntimeError(f"❌ **Failed after {MAX_RETRIES} retries:** {last_error}")


def call_azure_openai_api(
    user_prompt: str,
    system_prompt: str,
    api_key: str,
    endpoint: str,
    deployment_name: str,
    api_version: str = "2024-02-01",
) -> str:
    """
    Call Azure OpenAI API using the official OpenAI SDK with Azure config.

    Raises:
        RuntimeError: If the SDK is not installed or the API call fails.
    """
    if AzureOpenAI is None:
        raise RuntimeError(
            "The `openai` package is not installed. "
            "Run `pip install openai` to fix this."
        )

    try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint,
        )
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=8192,
        )
        return response.choices[0].message.content

    except Exception as e:
        error_msg = str(e).lower()
        if "authentication" in error_msg or "401" in error_msg:
            raise RuntimeError(
                "🔑 **Authentication failed.** Please verify your Azure OpenAI credentials."
            ) from e
        elif "429" in error_msg or "rate" in error_msg:
            raise RuntimeError(
                "⏳ **Rate limit exceeded.** Please wait a moment and retry."
            ) from e
        elif "timeout" in error_msg:
            raise RuntimeError(
                "🕐 **Request timed out.** Please try again."
            ) from e
        elif "404" in error_msg or "not found" in error_msg:
            raise RuntimeError(
                "🔍 **Deployment not found.** Check your Azure endpoint URL and deployment name."
            ) from e
        else:
            raise RuntimeError(f"❌ **Azure OpenAI Error:** {e}") from e


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator — Route to the right LLM based on user selection
# ─────────────────────────────────────────────────────────────────────────────
def call_llm(legacy_code: str, mode: str = "full") -> str:
    """
    High-level function: build prompts, select provider, call the LLM.

    Args:
        legacy_code: Raw legacy source code.
        mode: "full", "docs_only", or "python_only".

    Returns:
        Raw LLM response text.
    """
    language = st.session_state.get("selected_language", "RPGLE / AS400")
    system_prompt = build_system_prompt(language=language)
    user_prompt = build_user_prompt(legacy_code, language=language, mode=mode)
    provider = st.session_state.get("selected_model", "Gemini 1.5 Pro")

    if provider.startswith("Gemini"):
        api_key = st.session_state.get("gemini_api_key", "")
        if not api_key:
            raise RuntimeError("🔑 Please enter your **Gemini API Key** in the sidebar.")
        # Map display name to actual Gemini model ID
        model_map = {
            "Gemini Flash (Latest)": "gemini-flash-latest",
            "Gemini 1.5 Pro": "gemini-1.5-pro",
            "Gemini 1.5 Flash": "gemini-1.5-flash",
        }
        model_name = model_map.get(provider, "gemini-flash-latest")
        return call_gemini_api(user_prompt, system_prompt, api_key, model_name=model_name)

    elif provider.startswith("Azure"):
        api_key = st.session_state.get("azure_api_key", "")
        endpoint = st.session_state.get("azure_endpoint", "")
        deployment = st.session_state.get("azure_deployment", "")
        api_version = st.session_state.get("azure_api_version", "2024-02-01")
        if not all([api_key, endpoint, deployment]):
            raise RuntimeError(
                "🔑 Please enter your **Azure OpenAI credentials** (API key, endpoint, and deployment name) in the sidebar."
            )
        return call_azure_openai_api(
            user_prompt, system_prompt, api_key, endpoint, deployment, api_version
        )
    else:
        raise RuntimeError(f"Unknown model provider: {provider}")


# ─────────────────────────────────────────────────────────────────────────────
# Report Generator — Build downloadable markdown document
# ─────────────────────────────────────────────────────────────────────────────
def generate_report_markdown(
    legacy_code: str,
    sections: dict[str, str],
) -> str:
    """Create a polished markdown report combining all generated output."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    language = st.session_state.get("selected_language", "RPGLE / AS400")
    report = textwrap.dedent(f"""\
    # LegacyLens Analysis Report
    **Generated:** {now}
    **Model:** {st.session_state.get("selected_model", "N/A")}
    **Language:** {language}

    ---

    ## Original {language} Code
    ```
    {legacy_code}
    ```

    ---

    ## Executive Summary
    {sections.get("executive_summary", "N/A")}

    ---

    ## Technical Documentation
    {sections.get("technical_docs", "N/A")}

    ---

    ## Modernized Python Code
    {sections.get("python_code", "N/A")}

    ---
    *Report generated by LegacyLens — Legacy Code Explainer & Modernizer*
    """)
    return report


# ─────────────────────────────────────────────────────────────────────────────
# Session State Initialization
# ─────────────────────────────────────────────────────────────────────────────
def init_session_state() -> None:
    """Initialize all session state variables with sensible defaults."""
    defaults = {
        # API Keys
        "gemini_api_key": "",
        "azure_api_key": "",
        "azure_endpoint": "",
        "azure_deployment": "",
        "azure_api_version": "2024-02-01",
        # Model & language selection
        "selected_model": "Gemini Flash (Latest)",
        "selected_language": "RPGLE / AS400",
        # User input
        "rpgle_input": "",
        # Generated output sections
        "executive_summary": "",
        "technical_docs": "",
        "python_code": "",
        # Status flags
        "analysis_complete": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar UI
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar() -> None:
    """Render the sidebar with branding, configuration, and help section."""
    with st.sidebar:
        # ── Brand ─────────────────────────────────────────────────
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-icon">🔍</div>
                <div class="sidebar-brand-name">LegacyLens</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Model Selection ───────────────────────────────────────
        st.markdown('<div class="sidebar-section-label">🤖 Model Provider</div>', unsafe_allow_html=True)
        selected_model = st.selectbox(
            "Choose your LLM",
            options=["Gemini Flash (Latest)", "Gemini 1.5 Pro", "Gemini 1.5 Flash", "Azure GPT-4", "Azure GPT-4o"],
            index=0,
            label_visibility="collapsed",
            key="selected_model",
        )

        st.divider()

        # ── Language Selection ────────────────────────────────────
        st.markdown('<div class="sidebar-section-label">🖥️ Legacy Language</div>', unsafe_allow_html=True)
        st.selectbox(
            "Choose legacy language",
            options=SUPPORTED_LANGUAGES,
            index=0,
            label_visibility="collapsed",
            key="selected_language",
        )

        st.divider()

        # ── API Key Inputs — conditional based on provider ────────
        if selected_model.startswith("Gemini"):
            st.markdown('<div class="sidebar-section-label">🔐 Gemini API Key</div>', unsafe_allow_html=True)
            st.text_input(
                "Gemini API Key",
                type="password",
                placeholder="AIza...",
                label_visibility="collapsed",
                key="gemini_api_key",
                help="Get your API key from https://aistudio.google.com/app/apikey",
            )

            # Connection status indicator
            if st.session_state.get("gemini_api_key"):
                st.markdown(
                    '<span class="status-badge status-ready">● Key Entered</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<span class="status-badge status-waiting">○ Awaiting Key</span>',
                    unsafe_allow_html=True,
                )

        elif selected_model.startswith("Azure"):
            st.markdown('<div class="sidebar-section-label">🔐 Azure OpenAI Credentials</div>', unsafe_allow_html=True)
            st.text_input(
                "Azure API Key",
                type="password",
                placeholder="Enter your Azure API key",
                label_visibility="collapsed",
                key="azure_api_key",
            )
            st.text_input(
                "Endpoint URL",
                placeholder="https://your-resource.openai.azure.com/",
                label_visibility="collapsed",
                key="azure_endpoint",
                help="Your Azure OpenAI resource endpoint URL",
            )
            st.text_input(
                "Deployment Name",
                placeholder="gpt-4",
                label_visibility="collapsed",
                key="azure_deployment",
                help="The name of your Azure model deployment",
            )
            with st.expander("Advanced Settings"):
                st.text_input(
                    "API Version",
                    placeholder="2024-02-01",
                    label_visibility="collapsed",
                    key="azure_api_version",
                )

            # Connection status indicator
            if all([
                st.session_state.get("azure_api_key"),
                st.session_state.get("azure_endpoint"),
                st.session_state.get("azure_deployment"),
            ]):
                st.markdown(
                    '<span class="status-badge status-ready">● Credentials Set</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<span class="status-badge status-waiting">○ Incomplete</span>',
                    unsafe_allow_html=True,
                )

        st.divider()

        # ── How It Works Section ──────────────────────────────────
        st.markdown('<div class="sidebar-section-label">📖 How It Works</div>', unsafe_allow_html=True)
        st.markdown(
            """
            **LegacyLens** acts as a bridge between legacy
            mainframe systems and modern cloud architecture.

            **Supported Languages:**
            RPGLE, COBOL, JCL, PL/I, Natural/ADABAS, CL

            1. **Select** your legacy language
            2. **Paste** your mainframe code
            3. **Choose** your preferred AI model
            4. **Click** to generate documentation or Python code

            The AI analyzes your legacy code and produces:
            - 📝 **Executive Summary** — plain-English overview for stakeholders
            - 📋 **Technical Docs** — detailed variable & logic breakdown
            - 🐍 **Python Code** — modern, production-ready equivalent

            > *Your API keys are never stored on any server.
            > They exist only in your browser session.*
            """,
        )

        st.divider()

        # ── Footer ────────────────────────────────────────────────
        st.caption("LegacyLens v1.1.0 • Built with Streamlit")


# ─────────────────────────────────────────────────────────────────────────────
# Main Content UI
# ─────────────────────────────────────────────────────────────────────────────
def render_main_content() -> None:
    """Render the main workspace: header, input area, action buttons, output tabs."""

    # ── Hero Header ───────────────────────────────────────────────
    st.markdown(
        """
        <div class="hero-header">
            <div class="hero-title">🔍 LegacyLens</div>
            <div class="hero-subtitle">
                Transform cryptic legacy mainframe code (RPGLE, COBOL, JCL, PL/I & more)
                into clear documentation and modern Python — powered by AI.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Input Section ─────────────────────────────────────────────
    selected_lang = st.session_state.get("selected_language", "RPGLE / AS400")
    st.markdown(
        f'<div class="ll-card-title">📥 {selected_lang} Source Code</div>',
        unsafe_allow_html=True,
    )

    # "Load Sample Code" button
    col_sample, col_clear = st.columns([1, 1])
    with col_sample:
        if st.button(f"📄 Load {selected_lang} Sample", use_container_width=True, help=f"Load a demo {selected_lang} snippet to try the tool"):
            st.session_state["rpgle_input"] = SAMPLE_CODES.get(selected_lang, SAMPLE_RPGLE_CODE)
            st.rerun()
    with col_clear:
        if st.button("🗑️ Clear", use_container_width=True, help="Clear the code input area"):
            st.session_state["rpgle_input"] = ""
            st.session_state["analysis_complete"] = False
            st.session_state["executive_summary"] = ""
            st.session_state["technical_docs"] = ""
            st.session_state["python_code"] = ""
            st.rerun()

    # Code input text area — uses 'rpgle_input' as both session state key
    # and widget key so button handlers can set it directly.
    rpgle_code = st.text_area(
        "Paste your legacy code here",
        height=300,
        placeholder=f"Paste your {selected_lang} code here...\n\nOr click 'Load Sample' above to try a demo.",
        label_visibility="collapsed",
        key="rpgle_input",
    )

    # Show character count
    if rpgle_code:
        line_count = rpgle_code.count("\n") + 1
        st.caption(f"📊 {len(rpgle_code)} characters • {line_count} lines")

    st.markdown("---")

    # ── Action Buttons ────────────────────────────────────────────
    st.markdown(
        '<div class="ll-card-title">⚡ Actions</div>',
        unsafe_allow_html=True,
    )

    col_doc, col_python, col_full = st.columns(3)

    with col_doc:
        btn_docs = st.button(
            "📝 Generate Documentation",
            use_container_width=True,
            help="Generate Executive Summary and Technical Documentation only",
        )
    with col_python:
        btn_python = st.button(
            "🐍 Translate to Python",
            use_container_width=True,
            help="Generate modernized Python code only",
        )
    with col_full:
        btn_full = st.button(
            "🚀 Full Analysis",
            use_container_width=True,
            type="primary",
            help="Generate all outputs: Summary, Docs, and Python code",
        )

    # ── Handle Button Clicks ──────────────────────────────────────
    action_mode = None
    if btn_full:
        action_mode = "full"
    elif btn_docs:
        action_mode = "docs_only"
    elif btn_python:
        action_mode = "python_only"

    if action_mode:
        # ── Input Validation ──────────────────────────────────────
        is_valid, error_msg = validate_input(rpgle_code, selected_lang)
        if not is_valid:
            st.error(error_msg)
        else:
            # Show warnings for large inputs (but still proceed)
            check_input_warnings(rpgle_code)

            # Show estimated tokens
            est_input_tokens = estimate_tokens(rpgle_code) + 200  # +200 for system prompt
            st.caption(f"🪙 Estimated input: ~{est_input_tokens:,} tokens")

            with st.spinner("🔄 Analyzing your legacy code... This may take 15-30 seconds."):
                try:
                    raw_response = call_llm(rpgle_code, mode=action_mode)
                    sections = parse_llm_response(raw_response)

                    # Store results — clear stale data from other tabs
                    if action_mode == "full":
                        st.session_state["executive_summary"] = sections["executive_summary"]
                        st.session_state["technical_docs"] = sections["technical_docs"]
                        st.session_state["python_code"] = sections["python_code"]
                    elif action_mode == "docs_only":
                        st.session_state["executive_summary"] = sections["executive_summary"]
                        st.session_state["technical_docs"] = sections["technical_docs"]
                        st.session_state["python_code"] = ""  # Clear stale python
                    elif action_mode == "python_only":
                        st.session_state["executive_summary"] = ""  # Clear stale summary
                        st.session_state["technical_docs"] = ""     # Clear stale docs
                        st.session_state["python_code"] = sections["python_code"]

                    st.session_state["last_action_mode"] = action_mode
                    st.session_state["analysis_complete"] = True

                    # Check for truncated output
                    if sections.get("python_code_truncated"):
                        st.warning(
                            "⚠️ **Output may be truncated.** The Python code section "
                            "appears incomplete. Try using **Translate to Python** "
                            "separately, or split your input into smaller sections.",
                            icon="⚠️",
                        )
                        st.toast("⚠️ Analysis complete (output may be truncated)", icon="⚠️")
                    else:
                        st.toast("✅ Analysis complete!", icon="🎉")

                except RuntimeError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"❌ An unexpected error occurred: {e}")

    # ── Output Tabs ───────────────────────────────────────────────
    if st.session_state.get("analysis_complete"):
        st.markdown("---")
        st.markdown(
            '<div class="ll-card-title">📊 Analysis Results</div>',
            unsafe_allow_html=True,
        )

        last_mode = st.session_state.get("last_action_mode", "full")
        has_summary = bool(st.session_state.get("executive_summary", ""))
        has_docs = bool(st.session_state.get("technical_docs", ""))
        has_python = bool(st.session_state.get("python_code", ""))

        tab_summary, tab_tech, tab_python = st.tabs([
            "📝 Executive Summary",
            "📋 Technical Documentation",
            "🐍 Python Modernization",
        ])

        with tab_summary:
            summary = st.session_state.get("executive_summary", "")
            if summary and not summary.startswith("_No"):
                st.markdown(
                    """<div class="ll-card">"""
                    """<div class="ll-card-title">Executive Summary</div>"""
                    """</div>""",
                    unsafe_allow_html=True,
                )
                st.markdown(summary)
            else:
                if last_mode == "python_only":
                    st.markdown(
                        '<div style="text-align:center; padding:40px 20px; color:#666; '
                        'background:rgba(100,100,100,0.05); border-radius:10px; margin:10px 0;">'
                        '<div style="font-size:2rem; margin-bottom:10px;">📝</div>'
                        '<strong>Not generated in this run</strong><br>'
                        '<span style="font-size:0.85rem;">You selected <em>Translate to Python</em> only. '
                        'Use <strong>Generate Documentation</strong> or <strong>Full Analysis</strong> '
                        'to populate this tab.</span></div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.info("📝 Click **Generate Documentation** or **Full Analysis** to generate the executive summary.")

        with tab_tech:
            tech_docs = st.session_state.get("technical_docs", "")
            if tech_docs and not tech_docs.startswith("_No"):
                st.markdown(
                    """<div class="ll-card">"""
                    """<div class="ll-card-title">Technical Documentation</div>"""
                    """</div>""",
                    unsafe_allow_html=True,
                )
                st.markdown(tech_docs)
            else:
                if last_mode == "python_only":
                    st.markdown(
                        '<div style="text-align:center; padding:40px 20px; color:#666; '
                        'background:rgba(100,100,100,0.05); border-radius:10px; margin:10px 0;">'
                        '<div style="font-size:2rem; margin-bottom:10px;">📋</div>'
                        '<strong>Not generated in this run</strong><br>'
                        '<span style="font-size:0.85rem;">You selected <em>Translate to Python</em> only. '
                        'Use <strong>Generate Documentation</strong> or <strong>Full Analysis</strong> '
                        'to populate this tab.</span></div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.info("📋 Click **Generate Documentation** or **Full Analysis** to generate technical docs.")

        with tab_python:
            python_code = st.session_state.get("python_code", "")
            if python_code and not python_code.startswith("_No"):
                st.markdown(
                    """<div class="ll-card">"""
                    """<div class="ll-card-title">Modernized Python Code</div>"""
                    """</div>""",
                    unsafe_allow_html=True,
                )
                st.markdown(python_code)
            else:
                if last_mode == "docs_only":
                    st.markdown(
                        '<div style="text-align:center; padding:40px 20px; color:#666; '
                        'background:rgba(100,100,100,0.05); border-radius:10px; margin:10px 0;">'
                        '<div style="font-size:2rem; margin-bottom:10px;">🐍</div>'
                        '<strong>Not generated in this run</strong><br>'
                        '<span style="font-size:0.85rem;">You selected <em>Generate Documentation</em> only. '
                        'Use <strong>Translate to Python</strong> or <strong>Full Analysis</strong> '
                        'to populate this tab.</span></div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.info("🐍 Click **Translate to Python** or **Full Analysis** to generate Python code.")

        # ── Download Report Button ────────────────────────────────
        st.markdown("---")
        report_sections = {
            "executive_summary": st.session_state.get("executive_summary", ""),
            "technical_docs": st.session_state.get("technical_docs", ""),
            "python_code": st.session_state.get("python_code", ""),
        }

        # Only show download if there's actual content
        has_content = any(
            v and not v.startswith("_No") for v in report_sections.values()
        )
        if has_content:
            report_md = generate_report_markdown(rpgle_code, report_sections)
            col_dl, col_spacer = st.columns([1, 2])
            with col_dl:
                st.download_button(
                    label="📥 Download Full Report (.md)",
                    data=report_md,
                    file_name=f"legacylens_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

    # ── Footer ────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="ll-footer">
            Built with ❤️ using Streamlit • LegacyLens v1.1.0<br>
            <span style="font-size: 0.7rem;">
                Your API keys never leave your browser session.
                No data is stored on our servers.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Application Entry Point
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    """Main entry point — wire everything together."""
    inject_custom_css()
    init_session_state()
    render_sidebar()
    render_main_content()


if __name__ == "__main__":
    main()
