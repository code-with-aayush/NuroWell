# from groq import Groq

# client = Groq()
# completion = client.chat.completions.create(
#     model="gemma2-9b-it",
#     messages=[
#         {
#             "role": "user",
#             "content": "Pulse Rate: 73.0 bpm\n\nSpO2: 97.2 %\n\nHRV: 4.2 ms\n\nGSR: 45.0 µS \ngenerate a stress report for this following readings in this manner in starting name age then these readings then conclusion part and then precautions and how to improve the condition. gsr basline is 50 \n\n"
#         },
#         {
#             "role": "assistant",
#             "content": "## Stress Report\n\n**Name:**  Please provide your name.\n**Age:** Please provide your age.\n\n**Vitals:**\n\n* **Pulse Rate:** 73.0 bpm (This is within a normal range for most adults at rest.)\n* **SpO2:** 97.2% (This indicates good oxygen saturation levels.)\n* **HRV:** 4.2 ms (This is a relatively low HRV, suggesting potential stress or fatigue.)\n* **GSR:** 45.0 µS  (This indicates slightly elevated skin conductance, a sign of increased sympathetic nervous system activity often associated with stress. Your baseline GSR is 50 µS, so this reading is below baseline, further supporting the notion of stress.)\n\n**Conclusion:**\n\nBased on the provided vitals, you may be experiencing some stress. The low HRV and GSR reading below baseline point to elevated sympathetic nervous system activity, which is a physiological response to stress.\n\n**Precautions:**\n\n* **Monitor Stress Levels:** Pay attention to situations and thoughts that trigger stress, and find healthy ways to manage them.\n* **Practice Relaxation Techniques:**  Engage in activities like deep breathing exercises, meditation, or yoga to calm your nervous system.\n* **Prioritize Sleep:**  Ensure you're getting adequate sleep, as sleep deprivation can exacerbate stress.\n* **Maintain a Healthy Lifestyle:**  Eat a balanced diet, exercise regularly, and limit caffeine and alcohol intake, all of which contribute to overall well-being and stress management.\n\n**How to Improve Your Condition:**\n\n* **Identify Stressors:**  Pinpoint the specific sources of stress in your life and develop strategies to address them. This could involve time management, boundary setting, or seeking support from others.\n* **Cultivate Mindfulness:**  Practice being present in the moment and observe your thoughts and feelings without judgment. Mindfulness can help you better manage stress responses.\n* **Seek Professional Help:** If you're struggling to manage stress on your own, consider speaking with a therapist or counselor. They can provide guidance and support in developing coping mechanisms. \n\n\nRemember: It's important to acknowledge and address stress, as chronic stress can have negative impacts on your physical and mental health. \n"
#         }
#     ],
#     temperature=1,
#     max_completion_tokens=1024,
#     top_p=1,
#     stream=True,
#     stop=None,
# )

# for chunk in completion:
#     print(chunk.choices[0].delta.content or "", end="")




from groq import Groq

# Initialize the Groq client
client = Groq(api_key="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")

# Prompt user for input
name = input("Enter your name: ")
age = input("Enter your age: ")
pulse = input("Enter Pulse Rate (in bpm): ")
spo2 = input("Enter SpO2 (in %): ")
hrv = input("Enter HRV (in ms): ")
gsr = input("Enter GSR (in µS): ")

# Create the formatted message
user_prompt = f"""
Name: {name}
Age: {age}

Pulse Rate: {pulse} bpm
SpO2: {spo2} %
HRV: {hrv} ms
GSR: {gsr} µS

Generate a stress report based on these readings. Start with name and age, then include the vitals. After that, give a conclusion, precautions, and tips on how to improve the condition. Note: GSR baseline is 50 µS.
"""

# Send to Groq chat completion
completion = client.chat.completions.create(
    model="gemma2-9b-it",
    messages=[
        {"role": "user", "content": user_prompt}
    ],
    temperature=1,
    max_tokens=1024,
    top_p=1,
    stream=True,
)

# Print the streamed output
print("\n--- Stress Report ---\n")
for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")
