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
    initial_sidebar_state="collapsed",
)

# Custom CSS for polished UI
st.markdown("""
<style>
    /* Header styling */
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1e3a5f;
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }
    .sub-header {
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    /* Chat message containers */
    [data-testid="stChatMessage"] {
        padding: 1rem 1.25rem;
        border-radius: 12px;
        margin-bottom: 0.5rem;
    }
    /* User messages - subtle background */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 1px solid #bae6fd;
    }
    /* Assistant messages */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
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

    # Header
    st.markdown('<p class="main-header">✈️ AI Flight Booking Assistant</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Search flights, check status, and get schedules. Ask in natural language.</p>',
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
    if prompt := st.chat_input("Ask about flights, e.g. 'Flights from JFK to LAX' or 'Status of flight AA100'"):
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

    # Sidebar with tips (optional, shown as expander if we add sidebar later)
    with st.sidebar:
        st.markdown("### 💡 Try asking")
        st.markdown("- *Flights from JFK to LAX today*")
        st.markdown("- *Status of flight AA100*")
        st.markdown("- *Delta flights from Atlanta to Chicago*")
        st.markdown("---")
        st.caption("Uses OpenRouter and Aviationstack. Set OPENROUTER_API_KEY and CLIENTSECRET in secrets.")


if __name__ == "__main__":
    main()
