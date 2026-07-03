import os
import logging
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TECHNIQUE_PROMPTS = {
    "chain_of_thought": {
        "name": "Chain of Thought",
        "system": "You are an expert prompt engineer. Rewrite the user's prompt using Chain-of-Thought (CoT) prompting technique. This means explicitly instructing the model to think step-by-step, show reasoning, and break down complex problems into smaller logical steps before arriving at the final answer.",
        "instruction": "Rewrite the following prompt to use Chain-of-Thought reasoning. Add explicit instructions for step-by-step thinking, showing work, and logical decomposition. Return ONLY the optimized prompt."
    },
    "few_shot": {
        "name": "Few-Shot",
        "system": "You are an expert prompt engineer. Rewrite the user's prompt using Few-Shot prompting technique. This means providing 2-5 clear examples of input-output pairs that demonstrate the desired behavior before asking the model to perform the task.",
        "instruction": "Rewrite the following prompt to use Few-Shot prompting. Add 3-4 diverse, high-quality examples that demonstrate the expected input-output pattern. Return ONLY the optimized prompt."
    },
    "zero_shot": {
        "name": "Zero-Shot",
        "system": "You are an expert prompt engineer. Rewrite the user's prompt using Zero-Shot prompting technique. This means crafting a clear, self-contained instruction that requires no examples - the model must understand and execute the task from the instruction alone.",
        "instruction": "Rewrite the following prompt to be a clear, comprehensive zero-shot prompt. Make it unambiguous, specific, and complete so no examples are needed. Return ONLY the optimized prompt."
    },
    "role_prompting": {
        "name": "Role Prompting",
        "system": "You are an expert prompt engineer. Rewrite the user's prompt using Role Prompting technique. This means assigning a specific persona, expertise, and perspective to the model (e.g., 'You are a senior software architect with 20 years of experience...') to improve output quality.",
        "instruction": "Rewrite the following prompt using Role Prompting. Assign an appropriate expert persona with relevant credentials, perspective, and tone. Return ONLY the optimized prompt."
    },
    "react": {
        "name": "ReAct (Reasoning + Acting)",
        "system": "You are an expert prompt engineer. Rewrite the user's prompt using ReAct (Reasoning + Acting) technique. This means structuring the prompt to alternate between reasoning steps (thought) and actions (tool use, searches, calculations) in a loop until the task is complete.",
        "instruction": "Rewrite the following prompt using ReAct format. Structure it with Thought/Action/Observation cycles. Include explicit reasoning steps and action directives. Return ONLY the optimized prompt."
    }
}

EXPLANATION_PROMPT = """You are an expert prompt engineer. Explain why the optimized prompt is better than the original.

Original prompt:
{original}

Optimized prompt ({technique}):
{optimized}

Provide a clear, concise explanation covering:
1. What specific changes were made
2. Why those changes improve the prompt (reference prompting principles)
3. What types of tasks this technique is best suited for

Keep it under 200 words. Be specific, not generic."""


def call_openrouter(messages, max_tokens=2000, temperature=0.3):
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set in environment")
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Prompt Engineering Assistant"
    }
    
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    response = requests.post(
        f"{OPENROUTER_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )
    
    if response.status_code != 200:
        logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
        raise Exception(f"API error: {response.status_code} - {response.text}")
    
    data = response.json()
    return data["choices"][0]["message"]["content"]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/optimize", methods=["POST"])
def optimize_prompt():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        prompt = data.get("prompt", "").strip()
        technique = data.get("technique", "chain_of_thought")
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        
        if technique not in TECHNIQUE_PROMPTS:
            return jsonify({"error": f"Invalid technique: {technique}"}), 400
        
        tech = TECHNIQUE_PROMPTS[technique]
        
        messages = [
            {"role": "system", "content": tech["system"]},
            {"role": "user", "content": f"{tech['instruction']}\n\nOriginal prompt:\n{prompt}"}
        ]
        
        optimized = call_openrouter(messages, max_tokens=2000, temperature=0.3)
        
        return jsonify({
            "original": prompt,
            "optimized": optimized.strip(),
            "technique": tech["name"]
        })
    
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        return jsonify({"error": f"Optimization failed: {str(e)}"}), 500


@app.route("/api/explain", methods=["POST"])
def explain_prompt():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        original = data.get("original", "").strip()
        optimized = data.get("optimized", "").strip()
        technique = data.get("technique", "Chain of Thought")
        
        if not original or not optimized:
            return jsonify({"error": "Both original and optimized prompts required"}), 400
        
        messages = [
            {"role": "system", "content": "You are an expert prompt engineer explaining prompt improvements."},
            {"role": "user", "content": EXPLANATION_PROMPT.format(
                original=original,
                optimized=optimized,
                technique=technique
            )}
        ]
        
        explanation = call_openrouter(messages, max_tokens=1000, temperature=0.4)
        
        return jsonify({"explanation": explanation.strip()})
    
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Explanation error: {e}")
        return jsonify({"error": f"Explanation failed: {str(e)}"}), 500


@app.route("/api/techniques", methods=["GET"])
def get_techniques():
    return jsonify({
        key: {"name": value["name"]}
        for key, value in TECHNIQUE_PROMPTS.items()
    })


if __name__ == "__main__":
    if not OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY not set. Set it in .env file.")
    app.run(debug=True, host="0.0.0.0", port=5000)