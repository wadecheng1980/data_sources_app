import inspect
import textwrap
import streamlit as st
from pathlib import Path

import data_sources
from data_sources import big_query, snowflake, aws_s3_boto, google_sheet

from utils import ui, intro

DATA_SOURCES = {
    intro.INTRO_IDENTIFIER: {
        "module": intro,
        "secret_key": None,
        "docs_url": None,
        "get_connector": None,
    },
    "🔎  BigQuery": {
        "module": data_sources.big_query,
        "secret_key": "bigquery",
        "docs_url": "https://docs.streamlit.io/knowledge-base/tutorials/databases/bigquery",
        "get_connector": data_sources.big_query.get_connector,
        "tutorial": data_sources.big_query.tutorial,
        "tutorial_anchor": "#tutorial-connecting-to-bigquery",
    },
    "❄️ Snowflake": {
        "module": data_sources.snowflake,
        "secret_key": "snowflake",
        "docs_url": "https://docs.streamlit.io/knowledge-base/tutorials/databases/snowflake",
        "get_connector": data_sources.snowflake.get_connector,
        "tutorial": data_sources.snowflake.tutorial,
        "tutorial_anchor": "#tutorial-connecting-to-snowflake",
    },
    "📦 AWS S3": {
        "module": data_sources.aws_s3_boto,
        "secret_key": "aws_s3",
        "docs_url": "https://docs.streamlit.io/knowledge-base/tutorials/databases/aws-s3",
        "get_connector": data_sources.aws_s3_boto.get_connector,
        "tutorial": data_sources.aws_s3_boto.tutorial,
        "tutorial_anchor": "#tutorial-connecting-to-aws-s3",
    },
    "📝 Google Sheet": {
        "module": data_sources.google_sheet,
        "secret_key": "gsheets",
        "docs_url": "https://docs.streamlit.io/en/latest/tutorial/public_gsheet.html#connect-streamlit-to-a-public-google-sheet",
        "get_connector": data_sources.google_sheet.get_connector,
        "tutorial": data_sources.google_sheet.tutorial,
        "tutorial_anchor": "#tutorial-connecting-to-google-sheet",
    },
}

NO_CREDENTIALS_FOUND = """❌ **We couldn't find credentials for '`{}`' in your Streamlit Secrets.**   
Please follow our tutorial just below 👇"""

CREDENTIALS_FOUND_BUT_ERROR = """**❌ Credentials were found but there is an error.**  
While you have successfully filled in Streamlit secrets for the key `{}`,
we have not been able to connect to the data source. You might have forgotten some fields.  
            
Check the exception below 👇  
"""

PIPFILE_URL = "https://github.com/streamlit/data_sources_app/blob/main/Pipfile"
WHAT_NEXT = f"""## What next?


def has_data_source_key_in_secrets(data_source: str) -> bool:
    return DATA_SOURCES[data_source]["secret_key"] in st.secrets


def show_success(data_source: str):
    st.success(
        f"""👏 Congrats! You have successfully filled in your Streamlit secrets..  
    Below, you'll find a sample app that connects to {data_source} and its associated [source code](#code)."""
    )


def show_error_when_not_connected(data_source: str):

    st.error(
        NO_CREDENTIALS_FOUND.format(
            DATA_SOURCES[data_source]["secret_key"],
        )
    )

    st.write(f"### Tutorial: connecting to {data_source}")
    ui.load_keyboard_class()
    DATA_SOURCES[data_source]["tutorial"]()


def what_next():
    st.write(WHAT_NEXT)


def code(app):
    st.markdown("## Code")
    sourcelines, _ = inspect.getsourcelines(app)
    st.code(textwrap.dedent("".join(sourcelines[1:])), "python")


def connect(data_source):
    """Try connecting to data source.
    Print exception should something wrong happen."""

    try:
        get_connector = DATA_SOURCES[data_source]["get_connector"]
        connector = get_connector()
        return connector

    except Exception as e:

        st.sidebar.error("❌ Could not connect.")

        st.error(
            CREDENTIALS_FOUND_BUT_ERROR.format(DATA_SOURCES[data_source]["secret_key"])
        )

        st.exception(e)

        st.stop()


# If viewer clicks on page selector: Update query params to point to this page.
def change_page_url():
    """Update query params to reflect the selected page."""
    if st.session_state["page_selector"] == intro.INTRO_IDENTIFIER:
        st.experimental_set_query_params()
    else:
        st.experimental_set_query_params(data_source=st.session_state["page_selector"])


if __name__ == "__main__":

    st.set_page_config(page_title="Data Sources app", page_icon="🔌", layout="centered")

    # Infer selected page from query params.
    query_params = st.experimental_get_query_params()
    if "data_source" in query_params:
        page_url = query_params["data_source"][0]
        if page_url in DATA_SOURCES.keys():
            st.session_state["page_selector"] = page_url

    data_source = st.sidebar.selectbox(
        "Choose a data source",
        list(DATA_SOURCES.keys()),
        index=0,
        key="page_selector",
        on_change=change_page_url,
    )

    st.session_state.active_page = data_source
    if "data_sources_already_connected" not in st.session_state:
        st.session_state.data_sources_already_connected = list()

    if data_source == intro.INTRO_IDENTIFIER:
        show_code = False
        show_balloons = False

    else:
        show_code = True
        show_balloons = True

        # First, look for credentials in the secrets
        data_source_key_in_secrets = has_data_source_key_in_secrets(data_source)

        if data_source_key_in_secrets:
            connect(data_source)
            st.sidebar.success("✔ Connected!")
            show_success(data_source)
        else:
            st.sidebar.error("❌ Could not connect!")
            show_error_when_not_connected(data_source)
            st.caption(QUESTION_OR_FEEDBACK)
            st.stop()

    st.title('紅番隊淨桿統計')
    pick_player = st.selectbox('請選擇球員', ('高志遠', '鄭文瑋', '蔡武勳'))
    st.write('球員名稱', pick_player)

    def run_query(query):
    rows = conn.execute(query, headers=1)
    return rows

    sheet_url = st.secrets["public_gsheets_url"]
    rows = run_query(f'SELECT * FROM "{sheet_url}"')

    # Print results.
    for row in rows:
    st.write(f"{row.name} has a :{row.pet}:")
    
    # Display data source app
    data_source_app = DATA_SOURCES[st.session_state["active_page"]]["module"].app
    data_source_app()

    # Show source code and what next
    if show_code:
        code(data_source_app)
        what_next()

    st.caption(QUESTION_OR_FEEDBACK)
    
    
