import os
import json
from langchain_openai.chat_models.azure import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from ragas.metrics import context_recall, answer_relevancy, faithfulness
from ragas import evaluate
from datasets import Dataset

# 1. Set up AzureOpenAI chat model
llm = AzureChatOpenAI(
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),  # e.g. "gpt-35-turbo"
    temperature=0.0,
    openai_api_version=os.getenv("OPENAI_API_VERSION"),
)

# 2. Create a ChatPromptTemplate for structured extraction
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are an assistant that extracts fields for RAGAS evaluation."),
    ("user", """Extract JSON with these keys: question, answer, contexts (array), ground_truth, metrics (array of ragas metrics)
User input:
\"\"\"{user_input}\"\"\"
""")
])

# 3. Build the LLMChain
extraction_chain = LLMChain(llm=llm, prompt=prompt_template)

# 4. Available RAGAS mappings
available = {
    "context_recall": context_recall,
    "answer_relevancy": answer_relevancy,
    "faithfulness": faithfulness,
}

def evaluate_with_llm(user_text: str):
    # a. Have LLM extract structured JSON
    raw = extraction_chain.invoke({"user_input": user_text})
    parsed = json.loads(raw)

    # b. Filter only valid metrics
    selected = [available[m] for m in parsed["metrics"] if m in available]

    # c. Build RAGAS dataset
    dataset = Dataset.from_dict({
        "question": [parsed["question"]],
        "answer": [parsed["answer"]],
        "contexts": [parsed["contexts"]],
        "ground_truth": [parsed.get("ground_truth", "")]
    })

    # d. Evaluate with RAGAS
    res = evaluate(dataset, metrics=selected)

    return {
        "parsed_input": parsed,
        "evaluation": res.to_pandas().iloc[0].to_dict()
    }

# Example
if __name__ == "__main__":
    user_input = """
Hi, I need context recall and answer relevancy.
Question: What is the CIO view on Nvidia?
Context: Nvidia is viewed strongly by CIOs due to its AI leadership.
Ground truth: CIOs see Nvidia as strategic.
Answer: Nvidia is considered a key AI player and seen favorably.
"""
    result = evaluate_with_llm(user_input)
    print(json.dumps(result, indent=2))
