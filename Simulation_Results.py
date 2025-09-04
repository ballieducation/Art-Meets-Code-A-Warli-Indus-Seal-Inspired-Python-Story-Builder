import os, random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import kendalltau, entropy
from wordcloud import WordCloud
from collections import Counter
import matplotlib as mpl

# === Original Story Reference ===
reference_story = [s.strip() for s in """
Many years ago in a small Indian village, a farmer had the misfortune of owing a large sum of money to a village moneylender.
The moneylender, who was old and ugly, fancied the farmer's beautiful daughter.
So he proposed a bargain.
He said he would forgo the farmer's debt if he could marry the farmer's daughter.
Both the farmer and his daughter were horrified by the proposal.
So the cunning money lender suggested that they let providence decide the matter.
He told them that he would put a black pebble and a white pebble into an empty money bag.
Then the girl would have to pick one pebble from the bag.
If she picked the black pebble, she would become his wife and her father's debt would be written off.
If she picked the white pebble she need not marry him and her father's debt would still be written off.
But if she refused to pick a pebble, her father would be thrown into jail.
They were standing on a pebble-strewn path in the farmer's field.
As they talked, the moneylender bent over to pick up two pebbles.
As he picked them up, the sharp-eyed girl noticed that he had picked up two black pebbles and put them into the bag.
He then asked the girl to pick a pebble from the bag.
Now, imagine you were standing in the field. What would you have done if you had been the girl?
Careful analysis would produce three possibilities.
The girl should refuse to take a pebble.
The girl should show that there were two black pebbles in the bag and expose the moneylender as a cheat.
The girl should pick a black pebble and sacrifice herself in order to save her father.
This is what the girl actually did.
The girl put her hand into the moneybag and drew out a pebble.
Without looking at it, she fumbled and let it fall onto the pebble-strewn path where it was lost.
She said: "Oh, how clumsy of me! But if you look in the bag, you will know which pebble I picked."
Since the remaining pebble was black, it must be assumed that she picked the white one.
Thus the girl turned an impossible situation into an advantageous one.
The story teaches us to think out of the box, or think laterally.
""".split("\n") if s.strip()]

n_sentences = len(reference_story)
reference_order = list(range(n_sentences))

# === Personas ===
personas = {
    "Careful": {"dwell_mean": 3.0, "dwell_sd": 0.5, "swaps_mean": 2, "sus_mean": 80, "tlx_mean": 40, "coherence_mean": 8},
    "Balanced": {"dwell_mean": 2.0, "dwell_sd": 0.6, "swaps_mean": 4, "sus_mean": 72, "tlx_mean": 50, "coherence_mean": 6},
    "Fast": {"dwell_mean": 0.8, "dwell_sd": 0.3, "swaps_mean": 5, "sus_mean": 70, "tlx_mean": 55, "coherence_mean": 4},
    "TrialError": {"dwell_mean": 1.5, "dwell_sd": 0.7, "swaps_mean": 10, "sus_mean": 65, "tlx_mean": 60, "coherence_mean": 5}
}

N_RUNS = 1000


######################################################################
######################################################################
###########################################################################





#############################################################################
################################################################################
###################################################################################


# === Metric Functions ===
def planning_score(avg_dwell, swaps, placements):
    dwell_factor = min(1.0, avg_dwell / 3.0)
    rearr_rate = swaps / placements if placements > 0 else 1.0
    return 100 * (0.65 * dwell_factor + 0.35 * (1.0 - rearr_rate))

def session_health(ps, sus, tlx):
    return 0.5 * ps + 0.3 * sus + 0.2 * (100 - tlx)

def simulate_student(persona_name):
    p = personas[persona_name]
    
    # Dwell times
    dwell_times = np.maximum(0, np.random.normal(p["dwell_mean"], p["dwell_sd"], n_sentences))
    avg_dwell = dwell_times.mean()
    
    # Swaps + placements
    swaps = np.random.poisson(p["swaps_mean"])
    placements = n_sentences
    
    # Core scores
    ps = planning_score(avg_dwell, swaps, placements)
    sus = np.random.normal(p["sus_mean"], 5)
    tlx = np.random.normal(p["tlx_mean"], 7)
    sh = session_health(ps, sus, tlx)
    
    # Final story order (introduce mistakes)
    student_order = list(range(n_sentences))
    mistakes = int((100-ps)/20)
    for _ in range(mistakes):
        i, j = random.sample(range(n_sentences), 2)
        student_order[i], student_order[j] = student_order[j], student_order[i]
    
    # Order accuracy
    tau, _ = kendalltau(reference_order, student_order)
    coherence = np.random.normal(p["coherence_mean"], 1.0)
    
    # Extended metrics
    dwell_probs = dwell_times / dwell_times.sum() if dwell_times.sum() > 0 else np.ones(n_sentences)/n_sentences
    E = entropy(dwell_probs, base=2)  # Slot entropy
    OSI = 1 - swaps/(placements+swaps)  # Order stability
    DT_avg = avg_dwell
    SER = {"Careful": 0.8, "Balanced": 0.6, "Fast": 0.5, "TrialError": 0.4}[persona_name]
    U = 1.0
    CLI = 0.4 * (E/np.log2(n_sentences)) + 0.3 * (DT_avg/3.0) + 0.3 * (tlx/100)
    
    return {
        "Persona": persona_name,
        "PS": ps, "SUS": sus, "TLX": tlx, "SH": sh,
        "Tau": tau, "Coherence": coherence,
        "Utilization": U, "Entropy": E, "OSI": OSI,
        "DT_avg": DT_avg, "SER": SER, "CLI": CLI
    }

# === Run Simulation ===
results = [simulate_student(p) for p in personas for _ in range(N_RUNS//len(personas))]
df = pd.DataFrame(results)

# === Save Summary Table ===
df_summary = df.groupby("Persona").mean()
df_summary.to_csv("simulation_all_metrics_summary.csv")

# === Graphs ===
# 1. Boxplot PS
plt.figure(figsize=(6,4))
df.boxplot(column="PS", by="Persona")
plt.title("Planning Score by Persona")
plt.suptitle("")
plt.ylabel("Planning Score (0-100)")
plt.savefig("ps_by_persona.png", dpi=300)
plt.close()

# 2. Boxplot SH
plt.figure(figsize=(6,4))
df.boxplot(column="SH", by="Persona")
plt.title("Session Health by Persona")
plt.suptitle("")
plt.ylabel("Session Health (0-100)")
plt.savefig("sh_by_persona.png", dpi=300)
plt.close()

# 3. SUS Distribution
plt.figure(figsize=(6,4))
for persona in personas:
    df[df["Persona"]==persona]["SUS"].plot(kind="kde", label=persona)
plt.legend()
plt.title("SUS Distribution by Persona")
plt.xlabel("SUS (0-100)")
plt.savefig("sus_distribution.png", dpi=300)
plt.close()

# 4. TLX Distribution
plt.figure(figsize=(6,4))
for persona in personas:
    df[df["Persona"]==persona]["TLX"].plot(kind="kde", label=persona)
plt.legend()
plt.title("NASA-TLX Distribution by Persona")
plt.xlabel("TLX (0-100)")
plt.savefig("tlx_distribution.png", dpi=300)
plt.close()

# 5. Scatter PS vs Coherence
plt.figure(figsize=(6,4))
for persona in personas:
    subset = df[df["Persona"]==persona]
    plt.scatter(subset["PS"], subset["Coherence"], alpha=0.5, label=persona)
plt.xlabel("Planning Score")
plt.ylabel("Coherence")
plt.legend()
plt.title("Planning Score vs Coherence")
plt.savefig("ps_vs_coherence.png", dpi=300)
plt.close()

# 6. Synthetic Dwell Heatmap
dwell_example = np.random.rand(3,7) * 10
plt.figure(figsize=(7,3))
plt.imshow(dwell_example, cmap="Reds")
plt.colorbar(label="Dwell Intensity")
plt.title("Synthetic Dwell Heatmap (3x7 Slots)")
plt.savefig("heatmap_dwell.png", dpi=300)
plt.close()

# === Qualitative Feedback Graphs ===
feedback_comments = [
    "The card game was fun and engaging",
    "I liked using pictures more than text",
    "It was confusing sometimes where to place the cards",
    "Audio narration would be helpful",
    "Multilingual labels are very useful",
    "I felt motivated to complete the story",
    "The heatmap helps teachers see where students struggle",
    "The activity was more interactive than reading",
    "Hints should be added for difficult parts",
    "It was easy to understand the interface",
    "I enjoyed the activity more than static worksheets"
]

# Wordcloud
feedback_text = " ".join(feedback_comments)
font_path = mpl.get_data_path() + "/fonts/ttf/DejaVuSans.ttf"
wc = WordCloud(width=800, height=400, background_color="white", colormap="tab10", font_path=font_path).generate(feedback_text)
plt.figure(figsize=(8,4))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.tight_layout()
plt.savefig("feedback_wordcloud.png", dpi=300)
plt.close()

# Bar chart of keywords
feedback_responses = ["fun", "engaging", "pictures", "confusing", "audio", "multilingual",
                      "motivated", "heatmap", "interactive", "hints", "easy", "enjoyed",
                      "fun", "motivated", "fun", "interactive", "audio", "confusing"]
word_counts = Counter(feedback_responses)
labels, values = zip(*word_counts.most_common(10))
plt.figure(figsize=(8,4))
plt.bar(labels, values, color="skyblue")
plt.title("Most Common Qualitative Feedback Keywords")
plt.ylabel("Frequency")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("feedback_keywords_bar.png", dpi=300)
plt.close()
