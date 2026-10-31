from modules.meeting_analyzer import analyze_meeting

sample_transcript = """ Rashi: We have decided to launch our website on January 15.

Riya: I will prepare the marketing campaign by February 10.

Raj: I will complete website testing by June 12.
"""
result = analyze_meeting(sample_transcript)
print("\n Meeting Analysis")
print("-------------")
print(result)