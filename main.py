# suppress warnings
import warnings

warnings.filterwarnings("ignore")

# import libraries
import requests, os
import argparse
from PIL import Image


import gradio as gr
from together import Together
import textwrap


## FUNCTION 1: This Allows Us to Prompt the AI MODEL
# -------------------------------------------------
def prompt_llm(prompt, with_linebreak=False):
    # This function allows us to prompt an LLM via the Together API

    # model
    model = "meta-llama/Meta-Llama-3-8B-Instruct-Lite"

    # Calculate the number of tokens
    tokens = len(prompt.split())

    # Make the API call
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    output = response.choices[0].message.content

    if with_linebreak:
        # Wrap the output
        wrapped_output = textwrap.fill(output, width=50)

        return wrapped_output
    else:
        return output


## FUNCTION 2: This Allows Us to Generate Images
# -------------------------------------------------
def gen_image(prompt, width=256, height=256):
    # This function allows us to generate images from a prompt
    response = client.images.generate(
        prompt=prompt,
        model="black-forest-labs/FLUX.1-schnell-Free",  # Using a supported model
        steps=2,
        n=1,
    )
    image_url = response.data[0].url
    image_filename = "image.png"

    # Download the image using requests instead of wget
    response = requests.get(image_url)
    with open(image_filename, "wb") as f:
        f.write(response.content)
    img = Image.open(image_filename)
    img = img.resize((height, width))

    return img


## Function 3: This Allows Us to Create a Chatbot
# -------------------------------------------------
def bot_response_function(user_message, chat_history):
    # 1. YOUR CODE HERE - Add your external knowledge here
    # not really an external knowledge and hardcoded for now
    external_knowledge = """
    - Language in practice: English 
    - User proficiency: Intermediate
    - User's recent challenges: not_recorded_any_yet
    - Suggested_follow_up_topics: not_predicted_any_Yet
    """

    # 2. YOUR CODE HERE -  Give the LLM a prompt to respond to the user
    chatbot_prompt = f"""    
    # Language Learning Assistant Prompt

    ## Context & Role
    You are a supportive language learning assistant integrated into a speaking practice app. Users are practicing conversational skills with a partner, and you only appear when they need help getting unstuck.

    ## Your Purpose
    - Help users overcome speaking obstacles during practice sessions
    - Provide concise, actionable suggestions (max 40 tokens per response)
    - Keep users motivated and engaged in their practice

    ## Response Guidelines

    ### When to be Brief (Encouragement Mode)
    If the user seems to be practicing well or just sharing what they're doing:
    - Offer short, motivating phrases: "Great job!" "Keep going!" "You've got this!"
    - Acknowledge their progress: "Sounds like good practice!"

    ### When to be Helpful (Assistance Mode) 
    If the user indicates they're stuck, confused, or asking for help:
    - Provide specific, actionable advice
    - Suggest conversation starters or questions
    - Offer vocabulary or phrase alternatives
    - Give tips for continuing the conversation

    ### Scope of Assistance
    - You are ONLY allowed to help with queries directly related to language learning (vocabulary, grammar, phrasing, conversation starters, practice ideas).
    - If the user asks for help outside this scope (e.g., math, history, personal opinions on unrelated topics), you MUST politely decline, stating you can only assist with language practice. Example: "I can only help with language practice, sorry!"

    ### Tone
    - Consistently uplifting, energetic, positive, kind, and engaging.

    ### Key Constraints
    - **Conciseness is critical**: Responses must be around 40 tokens or fewer
    - **Stay focused**: Only help with language learning and speaking practice
    - **Be encouraging**: Maintain an uplifting, positive, energetic tone
    - **Ask engaging follow-ups** when appropriate to keep conversation flowing

    ## User Message
    {user_message}

    ## Response Strategy
    1. Determine if user needs encouragement or assistance
    2. Provide the most helpful response within token limit
    3. Include a brief follow-up question if space allows
    
    """

    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct-Lite",
        messages=[{"role": "user", "content": chatbot_prompt}],
    )
    response = response.choices[0].message.content

    # 3. YOUR CODE HERE - Generate image based on the response
    image_prompt = f"A {response} in a pop art style"
    image = gen_image(image_prompt)

    # Append the response and image to the chat history
    chat_history.append((user_message, response))
    return "", chat_history, image


if __name__ == "__main__":
    # args on which to run the script
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option", type=int, default=1)
    parser.add_argument("-k", "--api_key", type=str, default=None)
    args = parser.parse_args()

    # Get Client for your LLMs
    client = Together(api_key=args.api_key)

    # run the script
    if args.option == 1:
        ### Task 1: YOUR CODE HERE - Write a prompt for the LLM to respond to the user
        prompt = "write a 3 poetic lines that describes a cat licking its paw"

        # Get Response
        response = prompt_llm(prompt)

        print("\nResponse:\n")
        print(response)
        print("-" * 100)

    elif args.option == 2:
        ### Task 2: YOUR CODE HERE - Write a prompt for the LLM to generate an image
        prompt = "Create an image of a cat trying to lick its paw over the protective high tech gear the cat is wearing, therefore the cat is only licking the metal, not its pawhigh tech gear"

        print(f"\nCreating Image for your prompt: {prompt} ")
        img = gen_image(prompt=prompt, width=256, height=256)
        os.makedirs("results", exist_ok=True)
        img.save("results/image_option_2.png")
        print("\nImage saved to results/image_option_2.png\n")

    elif args.option == 3:
        ### Task 3: YOUR CODE HERE - Write a prompt for the LLM to generate text and an image
        text_prompt = "write a small blog post about things cat like to do"
        image_prompt = f"give me an image that represents this '{text_prompt}'"

        # Generate Text
        response = prompt_llm(text_prompt, with_linebreak=True)

        print("\nResponse:\n")
        print(response)
        print("-" * 100)

        # Generate Image
        print(f"\nCreating Image for your prompt: {image_prompt}... ")
        img = gen_image(prompt=image_prompt, width=256, height=256)
        img.save("results/image_option_3.png")
        print("\nImage saved to results/image_option_3.png\n")

    elif args.option == 4:
        # 4. Task 4: Create the chatbot interface (see bot_response_function for more details)
        with gr.Blocks(theme=gr.themes.Soft()) as app:
            gr.Markdown("## 🤖 AI Chatbot")
            gr.Markdown("Enter your message below and let the chatbot respond!")

            chatbot = gr.Chatbot()
            image_output = gr.Image(label="Generated Image")
            user_input = gr.Textbox(
                placeholder="Type your message here...", label="Your Message"
            )
            send_button = gr.Button("Send")

            send_button.click(
                bot_response_function,
                inputs=[user_input, chatbot],
                outputs=[user_input, chatbot, image_output],
            )
            user_input.submit(
                bot_response_function,
                inputs=[user_input, chatbot],
                outputs=[user_input, chatbot, image_output],
            )

        app.launch()
    else:
        print("Invalid option")