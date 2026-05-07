import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load env
load_dotenv()

from services.gemini_translate import generate_answer

async def run_test():
    query = "how to create user"
    chunks = [
        "## 1. How to Create a User Account in Suvit\nTo create a user, first login with the Primary Account. Go to Role Management in the sidebar, click '+ Add User' button on the top right, fill in user details (name, email, mobile, password), assign a role, and click 'Submit'.",
        "## 2. Difference between User and Client\nA User is a team member, while a Client is an external client account."
    ]
    
    print("Testing English answer generation...")
    ans_en = await generate_answer(query, chunks, "en")
    print("\n--- ENGLISH ANSWER ---")
    print(ans_en)
    print("----------------------\n")

    print("Testing Hindi (Hinglish) answer generation...")
    ans_hi = await generate_answer(query, chunks, "hi")
    print("\n--- HINDI ANSWER ---")
    print(ans_hi)
    print("--------------------\n")

if __name__ == "__main__":
    asyncio.run(run_test())
