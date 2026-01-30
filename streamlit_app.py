"""
AI Flight Booking Assistant - Streamlit App
Deployable on Streamlit Cloud (streamlit.io)
"""
import os
import json
from typing import Optional

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError
from openai import OpenAI
import requests

# Load .env for local dev; Streamlit Cloud uses st.secrets (injected below)
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

# Inject Streamlit Cloud secrets into environment so OpenAI and search_flights work
def _inject_secrets():
    try:
        for key in ("OPENROUTER_API_KEY", "CLIENTSECRET"):
            if key in st.secrets:
                os.environ[key] = str(st.secrets[key])
    except (AttributeError, TypeError, StreamlitSecretNotFoundError):
        pass

# Page config - must be first Streamlit command
st.set_page_config(
    page_title="AI Flight Booking Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished UI
st.markdown("""
<style>
    /* Root: subtle background and spacing */
    .stApp {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
    }
    /* Main block container - readable width on wide layout */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
    }
    /* Header card */
    .hero-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0c4a6e 100%);
        border-radius: 16px;
        padding: 1.75rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.15);
    }
    .main-header {
        font-size: 1.85rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 0 0 0.35rem 0;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .sub-header {
        color: #94a3b8;
        font-size: 0.95rem;
        margin: 0;
        line-height: 1.5;
    }
    /* Chat message containers */
    [data-testid="stChatMessage"] {
        padding: 1rem 1.25rem;
        border-radius: 14px;
        margin-bottom: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    /* User messages */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        border: 1px solid #7dd3fc;
    }
    /* Assistant messages */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    /* Chat input area - improved typing experience */
    [data-testid="stChatInput"] {
        padding: 1rem 0 1.5rem 0;
        background: linear-gradient(180deg, transparent 0%, rgba(248, 250, 252, 0.8) 100%);
    }
    [data-testid="stChatInput"] > div {
        background: #ffffff;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04);
        padding: 0.5rem;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    [data-testid="stChatInput"] > div:focus-within {
        border-color: #0ea5e9;
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15), 0 2px 8px rgba(0, 0, 0, 0.06);
    }
    [data-testid="stChatInput"] textarea {
        border: none !important;
        border-radius: 12px;
        padding: 0.875rem 1rem !important;
        min-height: 52px !important;
        font-size: 1rem !important;
        line-height: 1.5 !important;
        background: #f8fafc !important;
        box-shadow: none !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #64748b;
    }
    [data-testid="stChatInput"] textarea:focus {
        background: #ffffff !important;
        outline: none !important;
    }
    /* Send button inside chat input */
    [data-testid="stChatInput"] button {
        border-radius: 10px !important;
        font-weight: 500 !important;
    }
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #1e293b;
        font-weight: 600;
    }
    .tip-item {
        background: #fff;
        border-radius: 10px;
        padding: 0.65rem 1rem;
        margin-bottom: 0.5rem;
        border: 1px solid #e2e8f0;
        font-size: 0.9rem;
        color: #475569;
    }
    .tip-item:hover {
        border-color: #bae6fd;
        background: #f0f9ff;
    }
    /* Hide Streamlit branding for cleaner deploy */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Constants
MODEL = "gpt-4o-mini"
SYSTEM_MESSAGE = """
You are a friendly and helpful AI flight booking assistant. Your primary role is to help users search for flights, check flight status, and find flight schedules using real-time flight data from Aviationstack API.

When users ask about flights, flight schedules, or flight status, you should proactively use the search_flights tool to retrieve accurate, up-to-date information. You can search by:
- Flight number (e.g., "AA100")
- Departure and arrival airports (using IATA codes like JFK, LAX, LHR)
- Flight date (YYYY-MM-DD format)
- Airline (using IATA codes like AA, DL, UA)

Provide clear, concise, and helpful responses. When presenting flight information, format it in an easy-to-read manner. If flight information is unavailable or cannot be found, clearly inform the user. Always use the search_flights tool when users ask flight-related questions rather than making assumptions.
"""

SEARCH_FLIGHTS_FUNCTION = {
    "type": "function",
    "function": {
        "name": "search_flights",
        "description": "Search for real-time and historical flight information using Aviationstack API. "
                       "Use this when users ask about flight status, flight schedules, or want to search for flights. "
                       "You can search by flight number, departure/arrival airports, flight date, or airline.",
        "parameters": {
            "type": "object",
            "properties": {
                "flight_number": {
                    "type": "string",
                    "description": "Flight number in IATA format (e.g., 'AA100', 'DL200'). Leave empty if searching by route."
                },
                "dep_iata": {
                    "type": "string",
                    "description": "Departure airport IATA code (e.g., 'JFK', 'LAX', 'LHR'). Use 3-letter airport codes."
                },
                "arr_iata": {
                    "type": "string",
                    "description": "Arrival airport IATA code (e.g., 'JFK', 'LAX', 'LHR'). Use 3-letter airport codes."
                },
                "flight_date": {
                    "type": "string",
                    "description": "Flight date in YYYY-MM-DD format (e.g., '2026-01-29'). Optional, defaults to today if not specified."
                },
                "airline_iata": {
                    "type": "string",
                    "description": "Airline IATA code (e.g., 'AA' for American Airlines, 'DL' for Delta). Optional."
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
}


def search_flights(
    flight_number: Optional[str] = None,
    dep_iata: Optional[str] = None,
    arr_iata: Optional[str] = None,
    flight_date: Optional[str] = None,
    airline_iata: Optional[str] = None,
) -> str:
    """Search for flights using Aviationstack API."""
    api_key = os.getenv("CLIENTSECRET")
    if not api_key:
        return "Error: Aviationstack API key (CLIENTSECRET) not found in environment variables"

    base_url = "https://api.aviationstack.com/v1/flights"
    params = {"access_key": api_key}

    if flight_number:
        params["flight_iata"] = flight_number
    if dep_iata:
        params["dep_iata"] = dep_iata.upper()
    if arr_iata:
        params["arr_iata"] = arr_iata.upper()
    if flight_date:
        params["flight_date"] = flight_date
    if airline_iata:
        params["airline_iata"] = airline_iata.upper()

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("error"):
            return f"API Error: {data.get('error', {}).get('info', 'Unknown error')}"

        flights = data.get("data", [])
        if not flights:
            return "No flights found matching the search criteria."

        flight_info = []
        for flight in flights[:5]:
            flight_data = flight.get("flight", {})
            departure = flight.get("departure", {})
            arrival = flight.get("arrival", {})
            airline = flight.get("airline", {})

            info = {
                "flight_number": flight_data.get("iata", "N/A"),
                "airline": airline.get("name", "N/A"),
                "departure": {
                    "airport": departure.get("airport", "N/A"),
                    "iata": departure.get("iata", "N/A"),
                    "scheduled": departure.get("scheduled", "N/A"),
                    "estimated": departure.get("estimated", "N/A"),
                    "status": departure.get("status", "N/A"),
                },
                "arrival": {
                    "airport": arrival.get("airport", "N/A"),
                    "iata": arrival.get("iata", "N/A"),
                    "scheduled": arrival.get("scheduled", "N/A"),
                    "estimated": arrival.get("estimated", "N/A"),
                    "status": arrival.get("status", "N/A"),
                },
                "flight_status": flight.get("flight_status", "N/A"),
            }
            flight_info.append(info)

        return json.dumps(flight_info, indent=2)

    except requests.exceptions.RequestException as e:
        return f"Error fetching flight data: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def handle_tool_calls(message) -> list:
    """Handle tool calls from OpenAI response."""
    responses = []
    for tool_call in message.tool_calls:
        if tool_call.function.name == "search_flights":
            arguments = json.loads(tool_call.function.arguments)
            flight_info = search_flights(
                flight_number=arguments.get("flight_number"),
                dep_iata=arguments.get("dep_iata"),
                arr_iata=arguments.get("arr_iata"),
                flight_date=arguments.get("flight_date"),
                airline_iata=arguments.get("airline_iata"),
            )
            responses.append({
                "role": "tool",
                "content": flight_info,
                "tool_call_id": tool_call.id,
            })
    return responses


def get_openai_response(messages: list) -> str:
    """Call OpenAI-compatible API (OpenRouter) with tool support; returns final assistant text."""
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key,
    )
    max_iterations = 5
    iteration = 0
    assistant_message = None
    current_messages = list(messages)

    while iteration < max_iterations:
        response = client.chat.completions.create(
            model=MODEL,
            messages=current_messages,
            tools=[SEARCH_FLIGHTS_FUNCTION],
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message

        assistant_dict = {
            "role": assistant_message.role,
            "content": assistant_message.content or "",
        }
        if assistant_message.tool_calls:
            assistant_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in assistant_message.tool_calls
            ]

        current_messages.append(assistant_dict)

        if assistant_message.tool_calls:
            tool_responses = handle_tool_calls(assistant_message)
            current_messages.extend(tool_responses)
            iteration += 1
        else:
            return assistant_message.content or ""

    return (
        assistant_message.content
        if assistant_message and assistant_message.content
        else "I apologize, but I'm having trouble processing your request. Please try again."
    )


def main():
    _inject_secrets()

    # Hero header
    st.markdown(
        '<div class="hero-card">'
        '<p class="main-header">✈️ AI Flight Booking Assistant</p>'
        '<p class="sub-header">Search flights, check status, and get schedules. Ask in natural language.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask about flights… e.g. JFK to LAX or status of AA100"):
        # Append user message and display
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Build messages for API (system + history + current)
        api_messages = [{"role": "system", "content": SYSTEM_MESSAGE}]
        for m in st.session_state.messages:
            api_messages.append({"role": m["role"], "content": m["content"]})

        # Get assistant response with spinner
        with st.chat_message("assistant"):
            with st.spinner("Searching flights..."):
                try:
                    response_text = get_openai_response(api_messages)
                except Exception as e:
                    response_text = f"Sorry, an error occurred: {str(e)}"
            st.markdown(response_text)

        st.session_state.messages.append({"role": "assistant", "content": response_text})

    # Sidebar with tips
    with st.sidebar:
        st.markdown("### 💡 Try asking")
        st.markdown(
            '<div class="tip-item">Flights from JFK to LAX today</div>'
            '<div class="tip-item">Status of flight AA100</div>'
            '<div class="tip-item">Delta flights from Atlanta to Chicago</div>',
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.caption("Powered by OpenRouter + Aviationstack. Set OPENROUTER_API_KEY and CLIENTSECRET in secrets.")


if __name__ == "__main__":
    main()
