from typing import List, Dict
from pydantic import BaseModel
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_openai import ChatOpenAI


# 1. Schema
class OutputSchema(BaseModel):
    questions: List[str]
    answers: List[str]
    missing: bool
    missing_parameters: Dict[str, str]


# 2. Parser
parser = JsonOutputParser(pydantic_object=OutputSchema)

# Escape braces so LangChain doesn’t treat them as template variables
format_instructions = parser.get_format_instructions().replace("{", "{{").replace("}", "}}")

# 3. Templates
system_temp = SystemMessagePromptTemplate.from_template(
    "You are a helpful assistant. Answer in strict JSON format:\n" + format_instructions
)
human_temp = HumanMessagePromptTemplate.from_template("{user_input}")

# 4. Prompt
chat_prompt = ChatPromptTemplate.from_messages([system_temp, human_temp])

# 4. LLM & Chain
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.5,
    openai_api_key=OPENAI_API_KEY
)

# 6. Chain
chain = chat_prompt | llm | parser

# 7. Run
result = chain.invoke({"user_input": "What questions should I ask to evaluate sales performance?"})
print(result)
print(type(result))
import json
# print(result.questions, result.answers, result.missing, result.missing_parameters)
print(json.dumps(result, indent=2))



