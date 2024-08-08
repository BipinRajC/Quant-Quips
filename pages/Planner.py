import streamlit as st
import os
import json
import pandas as pd
from groq import Groq

# Set up the page configuration
st.set_page_config(page_title="Smart Financial Planner", page_icon="💰", layout="wide")

# Load configuration data for Groq API key
working_dir = os.path.dirname(os.path.abspath(__file__))
config_data = json.load(open(f"{working_dir}/config.json"))
GROQ_API_KEY = config_data["GROQ_API_KEY"]

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)
MODEL = 'llama3-groq-70b-8192-tool-use-preview'

# Function to evaluate mathematical expressions
def calculate(expression):
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression)
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": f"Invalid expression: {str(e)}"})

def format_as_table(calculation_result, description="Calculation Result"):
    """Format the calculation result as a markdown table."""
    markdown_table = f"""
| Description       | Value   |
|-------------------|---------|
| {description} | {calculation_result} |
"""
    return markdown_table

# Function to run a conversation with Groq AI
def run_conversation(user_prompt):
    """Run the conversation with the Groq AI model to generate financial plans."""
    messages = [
        {
            "role": "system",
            "content": "You are a financial planner assistant. Use the available tools to perform calculations and provide detailed investment plans to achieve the user's financial goals. Provide neatly formatted responses with detailed explanations.",
        },
        {
            "role": "user",
            "content": user_prompt,
        }
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Evaluate a mathematical expression",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "The mathematical expression to evaluate",
                        }
                    },
                    "required": ["expression"],
                },
            },
        }
    ]
    
    # Create the first response from the Groq model
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=4096
    )

    response_message = response.choices[0].message
    tool_calls = getattr(response_message, 'tool_calls', None)  # Use getattr to access tool_calls

    if tool_calls:
        available_functions = {
            "calculate": calculate,
        }
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions.get(function_name)
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                expression=function_args.get("expression")
            )
            # Append the tool response as if it was from the assistant
            messages.append(
                {
                    "role": "assistant",
                    "content": None,
                    "function_call": {
                        "name": function_name,
                        "arguments": json.dumps(function_args),
                    }
                }
            )
            messages.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                }
            )
        # Now, get the final response after the tool calls
        second_response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )
        return second_response.choices[0].message.content
    else:
        # Return content directly if no tools are invoked
        return response_message.content
    
def run_conversation_with_table(user_prompt):
    """Run the conversation and format the result as a markdown table."""
    # First, run the conversation to get the raw calculation result
    raw_result = run_conversation(user_prompt)
    
    # Now, structure the result as a markdown table
    formatted_table = format_as_table(raw_result)
    
    return formatted_table

# Streamlit User Interface
st.title("Smart Financial Planner")
st.write("Enter your financial goals and relevant details to get a customized investment plan.")

# User Inputs for financial planning
goal_prompt = st.text_area("Describe your financial goals (e.g., buying a house, saving for retirement):")
monthly_income = st.number_input("Monthly Disposable Income (in INR):", min_value=0.0, step=100.0, value=2000.0)
inflation_rate = st.number_input("Inflation Rate (%):", min_value=0.0, max_value=100.0, step=0.1, value=3.0)
tax_rate = st.number_input("Taxation Rate (%):", min_value=0.0, max_value=100.0, step=0.1, value=20.0)

# Prompt generation based on user input
user_prompt = f"""
My financial goal is: {goal_prompt}.
My monthly disposable income is {monthly_income} INR.
The expected inflation rate is {inflation_rate}%, and the taxation rate is {tax_rate}%.
Please provide an investment plan to achieve this goal.
"""

# Button to generate the financial plan
if st.button("Get Financial Plan"):
    with st.spinner("Generating your financial plan..."):
        plan = run_conversation(user_prompt)
        st.subheader("AI-Generated Financial Plan")
        st.write(plan)
        formedPlan = run_conversation_with_table(plan)
        st.write(formedPlan)

# Disclaimer
st.write("\"This tool is for educational purposes only. Please consult with a certified financial planner before making any investment decisions.\"")
