# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 20:34:45 2025

@author: balli
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Sep  1 12:20:43 2025

@author: balli
"""

# -*- coding: utf-8 -*-
"""
Story Builder + Planning Analytics (SUS/TLX + Session Health)
- Separate popups:
  • Show Final Story  -> story-only view, Save Story Text
  • Analytics         -> metrics-only view, Save Logs (CSV+JSON)
- logs each move (card, from→to, time)
- tracks rearrangements & dwell time
- Planning Score (dwell↑, rearrange↓). Auto-Fill excluded from score
- heatmap overlay (press H)
- Evaluate (SUS/TLX) popup
- Session Health = 0.50*Planning + 0.30*SUS + 0.20*(100 - TLX)

Your Planning Score (0–100)

The score comes from two things:

Looking time (65% of the score)

When your mouse hovers over a slot, we count that as “looking/thinking.”

We average this across all slots.

If you look about 3 seconds per slot, you get full points for this part.
(More than 3s doesn’t add extra; less gives fewer points.)

Shuffling penalty (35% of the score)

Every time you drag a card from one slot to another slot, that’s a rearrangement (a “swap”).

We compare how many swaps you did to how many cards you placed manually from the deck.

Fewer swaps per placement = more points for this part.

Note: Auto-Fill placements are not counted here, so they don’t boost this score unfairly.

Then we combine them:

65% from looking time (more looking → higher)

35% from low shuffling (fewer swaps → higher)

Tiny examples

Example A (middle score)

You looked ~1.5 s per slot → that’s half of the “looking” credit.

You made 10 placements and 5 swaps → swaps/placements = 0.5, so you keep half of the stability credit.

Final ≈ 50/100.

Example B (excellent score)

You looked ~3 s per slot → full looking credit.

10 placements, 1 swap → swaps/placements = 0.1, so you keep 90% of stability credit.

Final ≈ 97/100.

How to raise your score (in practice)

Hover and compare a few slots before you drop a card.

Place once, adjust rarely. Avoid slot-to-slot shuffling.

If you must change, replace from deck rather than swapping many times.

Quick reminders

The heatmap (H key) shows where you spent time looking—deeper red = more attention.

SUS (usability) and NASA-TLX (workload) are separate measures; they don’t change your Planning Score, but together they explain why planning was easy/hard.


"""
import pygame, os, sys, random, re, time, json, csv
from collections import defaultdict

# === CONFIG ===
CARD_FOLDER = "cards"
SCREEN_SIZE = (1200, 800)
CARD_SIZE = (130, 180)
BUTTON_BAR_Y = SCREEN_SIZE[1] - 80  
POPUP_BTN_Y = SCREEN_SIZE[1] - 80   # move popup buttons up by 20px
SLOTS_ROWS, SLOTS_COLS = 3, 7  # 21 slots
SLOT_SIZE = CARD_SIZE
SLOT_MARGIN = 10
DECK_POS = (20, 50)  # position of deck pile
LOG_DIR = "logs"

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Story Builder (Analytics Edition)")
font = pygame.font.SysFont("arial", 22)
small_font = pygame.font.SysFont("arial", 18)
big_font = pygame.font.SysFont("arial", 32, bold=True)
clock = pygame.time.Clock()

# === Utility: Clean filename into title ===

##################################################3
################################################333
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller .exe """
    try:
        # When bundled by PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        # When running as normal .py
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)




###################################################3
import os, sys
import pygame

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        base_path = sys._MEIPASS  # temp folder for PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def show_splash_screen():
    splash_bg = (255, 255, 255)  # White background
    screen.fill(splash_bg)

    # Try multiple logo formats
    logo = None
    for ext in ["png", "jpg", "jpeg"]:
        try:
            logo_path = resource_path(f"logo.{ext}")
            if os.path.exists(logo_path):
                logo = pygame.image.load(logo_path)
                break
        except:
            continue

    if logo:
        # Resize logo dynamically to 25% of screen width
        max_width = SCREEN_SIZE[0] // 4
        scale = max_width / logo.get_width()
        new_size = (int(logo.get_width() * scale), int(logo.get_height() * scale))
        logo = pygame.transform.smoothscale(logo, new_size)

    # Fonts (dark for white background)
    title = big_font.render("Write A Story From Cards", True, (30, 30, 60))
    subtitle = small_font.render("Developed by Balwinder Singh", True, (50, 50, 70))
    info = small_font.render("Educational Storytelling Project", True, (70, 70, 90))

    start_time = pygame.time.get_ticks()
    duration = 3000  # 3 seconds

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                running = False

        screen.fill(splash_bg)

        # Draw logo in center
        if logo:
            screen.blit(logo, (SCREEN_SIZE[0]//2 - logo.get_width()//2, 120))

        # Draw texts
        screen.blit(title, (SCREEN_SIZE[0]//2 - title.get_width()//2, 340))
        screen.blit(subtitle, (SCREEN_SIZE[0]//2 - subtitle.get_width()//2, 400))
        screen.blit(info, (SCREEN_SIZE[0]//2 - info.get_width()//2, 440))

        pygame.display.flip()
        clock.tick(60)

        if pygame.time.get_ticks() - start_time > duration:
            running = False





#######################################################
def filename_to_title(filename):
    name, _ = os.path.splitext(filename)
    cleaned = re.sub(r"^\d+[-_ ]*", "", name)  # strip numeric prefix
    cleaned = cleaned.replace("_", " ").replace("-", " ")
    return cleaned.strip().title() if cleaned.strip() else name.title()

def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)

# === Load Cards into Deck ===
##################################################################################################################
###############################################

def load_cards(folder):
    folder = resource_path(folder)  # important for .exe

    if not os.path.isdir(folder):
        os.makedirs(folder, exist_ok=True)

    files = sorted([f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))])
    deck = []

    for file in files[:21]:  # load up to 21 cards
        path = resource_path(os.path.join(folder, file))
        try:
            img = pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"Warning: could not load {file}: {e}")
            continue

        img = pygame.transform.smoothscale(img, CARD_SIZE)
        title = filename_to_title(file)
        card_id = os.path.splitext(file)[0]  # filename base = ID
        deck.append({"image": img, "title": title, "id": card_id})

    random.shuffle(deck)  # shuffle initial deck
    return deck





########################################
##########################################
def load_cards1(folder):
    if not os.path.isdir(folder):
        os.makedirs(folder, exist_ok=True)
    files = sorted([f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))])
    deck = []
    for file in files[:21]:
        path = os.path.join(folder, file)
        try:
            img = pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"Warning: could not load {file}: {e}")
            continue
        img = pygame.transform.smoothscale(img, CARD_SIZE)
        title = filename_to_title(file)
        card_id = os.path.splitext(file)[0]  # filename base = ID
        deck.append({"image": img, "title": title, "id": card_id})
    random.shuffle(deck)  # shuffle initial deck
    return deck
#########################################################################################################
##################################################################################################
###################################################################################################
# === Create Slots ===
def create_slots():
    slots = []
    start_x = (SCREEN_SIZE[0] - (SLOTS_COLS * SLOT_SIZE[0] + (SLOTS_COLS - 1) * SLOT_MARGIN)) // 2
    start_x = start_x + 70
    start_y = 50
    for r in range(SLOTS_ROWS):
        for c in range(SLOTS_COLS):
            x = start_x + c * (SLOT_SIZE[0] + SLOT_MARGIN)
            y = start_y + r * (SLOT_SIZE[1] + SLOT_MARGIN)
            slots.append({"rect": pygame.Rect(x, y, SLOT_SIZE[0], SLOT_SIZE[1]), "card": None})
    return slots

# === Draw helpers ===
def draw_slots(slots, dragging_card):
    for i, slot in enumerate(slots):
        pygame.draw.rect(screen, (200, 200, 200), slot["rect"], 3)
        num_text = font.render(str(i + 1), True, (180, 180, 180))
        screen.blit(num_text, (slot["rect"].x + 5, slot["rect"].y + 5))
        if slot["card"] and slot["card"] != dragging_card:
            screen.blit(slot["card"]["image"], slot["rect"])

def draw_deck(deck, dragging_card):
    if deck:
        top_card = deck[-1]  # top card is last in list
        if top_card != dragging_card:
            rect = pygame.Rect(DECK_POS[0], DECK_POS[1], CARD_SIZE[0], CARD_SIZE[1])
            screen.blit(top_card["image"], rect)

        # deck counter
        counter_text = f"Deck: {len(deck)} cards left"
        label = small_font.render(counter_text, True, (200, 200, 200))
        screen.blit(label, (DECK_POS[0], DECK_POS[1] + CARD_SIZE[1] + 5))

        # wrapped top-card title
        title = f"Title: {top_card['title']}"
        max_width = CARD_SIZE[0]
        words = title.split()
        lines, current_line = [], ""
        for w in words:
            test = (current_line + " " + w) if current_line else w
            if small_font.render(test, True, (180, 220, 180)).get_width() <= max_width:
                current_line = test
            else:
                lines.append(current_line); current_line = w
        if current_line: lines.append(current_line)
        y_offset = CARD_SIZE[1] + 25
        for line in lines:
            text_surface = small_font.render(line, True, (180, 220, 180))
            screen.blit(text_surface, (DECK_POS[0], DECK_POS[1] + y_offset))
            y_offset += 20
    else:
        label = small_font.render("Deck Empty", True, (200, 200, 200))
        screen.blit(label, (DECK_POS[0], DECK_POS[1] + CARD_SIZE[1] + 5))

def draw_button1(rect, text):
    pygame.draw.rect(screen, (50, 120, 200), rect, border_radius=8)
    label = font.render(text, True, (255, 255, 255))
    screen.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))
    
#############################################33
################################################3
def draw_button(rect, text, enabled=True):
    # Gray out when disabled, keep everything else the same
    color = (50, 120, 200) if enabled else (110, 110, 110)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    label = font.render(text, True, (255, 255, 255))
    screen.blit(
        label,
        (rect.centerx - label.get_width() // 2,
         rect.centery - label.get_height() // 2)
    )






#################################################3
######################################################    
    

def draw_tooltip(text, pos):
    tooltip_font = small_font
    label = tooltip_font.render(text, True, (0, 0, 0))
    padding = 6
    rect = label.get_rect()
    rect.topleft = (pos[0] + 12, pos[1] - rect.height - 12)
    pygame.draw.rect(screen, (255, 255, 200), (rect.x - padding, rect.y - padding,
                                               rect.width + 2*padding, rect.height + 2*padding))
    pygame.draw.rect(screen, (0, 0, 0), (rect.x - padding, rect.y - padding,
                                         rect.width + 2*padding, rect.height + 2*padding), 1)
    screen.blit(label, rect)

# === Analytics / logging ===
def log_event(analytics, kind, **kwargs):
    t = time.perf_counter() - analytics["t0"]
    row = {"t": round(t, 3), "event": kind}
    row.update(kwargs)
    analytics["move_log"].append(row)

def hovered_slot_index(slots, mx, my):
    for i, s in enumerate(slots):
        if s["rect"].collidepoint(mx, my):
            return i
    return None

def update_dwell(analytics, current_hover_idx, dt):
    prev = analytics["hover_idx"]
    if current_hover_idx is not None:
        analytics["slot_dwell"][current_hover_idx] += dt
        if prev != current_hover_idx:
            analytics["slot_views"][current_hover_idx] += 1
    analytics["hover_idx"] = current_hover_idx

# === SUS / NASA-TLX ===
SUS_ITEMS = [
    "I think that I would like to use this system frequently.",
    "I found the system unnecessarily complex.",
    "I thought the system was easy to use.",
    "I think that I would need the support of a technical person to be able to use this system.",
    "I found the various functions in this system were well integrated.",
    "I thought there was too much inconsistency in this system.",
    "I would imagine that most people would learn to use this system very quickly.",
    "I found the system very cumbersome to use.",
    "I felt very confident using the system.",
    "I needed to learn a lot of things before I could get going with this system."
]
TLX_KEYS = ["Mental Demand","Physical Demand","Temporal Demand","Performance","Effort","Frustration"]

def compute_sus(responses_1to5):
    if not responses_1to5 or len(responses_1to5) != 10 or any(r is None for r in responses_1to5):
        return None
    score = 0
    for i, r in enumerate(responses_1to5, start=1):
        score += (r - 1) if i % 2 == 1 else (5 - r)
    return round(score * 2.5, 1)

def compute_tlx_avg(scales_0_100):
    if not scales_0_100:
        return None
    vals = [max(0, min(100, int(scales_0_100[k]))) for k in TLX_KEYS]
    return round(sum(vals) / len(vals), 1)

def compute_planning_score(analytics):
    """Reward average dwell, penalize rearrangements per MANUAL placement (auto-fill excluded)."""
    placements_manual = analytics.get("placements_from_deck", 0)
    rearr = analytics.get("rearrangements_total", 0)
    avg_dwell = (sum(analytics["slot_dwell"]) / max(1, SLOTS_ROWS*SLOTS_COLS))
    dwell_factor = min(1.0, avg_dwell / 3.0)  # ~3s/slot = full credit
    rearr_rate = min(1.0, rearr / placements_manual) if placements_manual else (1.0 if rearr else 0.0)
    score = 100 * (0.65 * dwell_factor + 0.35 * (1.0 - rearr_rate))
    return int(round(score))

def compute_session_health(analytics):
    planning = compute_planning_score(analytics) or 0
    sus = analytics.get("sus_score") or 0
    tlx = analytics.get("tlx_avg") if analytics.get("tlx_avg") is not None else 100
    return round(0.50*planning + 0.30*sus + 0.20*(100 - tlx), 1)

def draw_heatmap(slots, analytics):
    dw = analytics["slot_dwell"]
    mx = max(dw) if dw else 0.0
    if mx <= 0: return
    for i, s in enumerate(slots):
        a = int(180 * (dw[i] / mx))  # alpha by dwell
        overlay = pygame.Surface((s["rect"].width, s["rect"].height), pygame.SRCALPHA)
        overlay.fill((255, 80, 80, a))  # reddish
        screen.blit(overlay, s["rect"].topleft)

def generate_story_text(slots):
    titles = [slot["card"]["title"] for slot in slots if slot["card"]]
    return ". ".join(titles) + "." if titles else "(No story yet)"


##########################################################
##########################################################
EXPECTED_SEQUENCE = [
    "Indian Village", "A Farmer", "Farmer'S Beautiful Daughter",
    "Money Lender", "Ledger Of Money Lender",
    "If Dept Is Not Paid Then Go To Jail,  Threat By Money Lander",
    "Bargain Proposed By Money Lander", "Two Pebbles", "Money Bag",
    "Out Of Two Only One Pebble In Hand", "Observe What Money Landder Do",
    "Put  Two Back Pebble In Money Bag Instead Of Putting One Black And One White And Close Money Bag",
    "Picks A Pebble From Out Of Two Pebble  In Money Bag",
    "Farmer'S Daughter Drop Pebble On Pebble Street", "Pebble Path",
    "Minimal Evidence (Use What Remains (The Leftover Pebble) To Prove The Truth)",
    "Change The Frame (Redefine The Rules Of Judgment So The Problem Is Solved Indirectly)",
    "Exploit Symmetry (Turn The Cheater’S Identical Choices Into Proof That Protects You)",
    "Third Option Create A New Way Beyond Two Bad Options"
]

def auto_story_quality(analytics, slots):
    """Compute a 0–9 story quality score automatically based on sequence, dwell, and stability."""
    # --- Factor 1: completeness ---
    filled_titles = [s["card"]["title"] for s in slots if s["card"]]
    completeness = len(filled_titles) / len(EXPECTED_SEQUENCE)

    # --- Factor 2: dwell time attention (target ~3s) ---
    avg_dwell = sum(analytics["slot_dwell"]) / max(1, len(slots))
    dwell_factor = min(1.0, avg_dwell / 3.0)

    # --- Factor 3: rearrangements penalty ---
    manual_places = analytics.get("placements_from_deck", 0)
    rearr = analytics.get("rearrangements_total", 0)
    stability = 1.0
    if manual_places > 0:
        stability = 1.0 - min(1.0, rearr / manual_places)

    # --- Factor 4: sequence accuracy ---
    seq_matches = sum(1 for i, t in enumerate(filled_titles) if i < len(EXPECTED_SEQUENCE) and t == EXPECTED_SEQUENCE[i])
    seq_factor = seq_matches / max(1, len(EXPECTED_SEQUENCE))

    # Combine weighted factors → 0–9 scale
    raw_score = (0.35 * completeness + 0.25 * dwell_factor + 0.20 * stability + 0.20 * seq_factor) * 9.0
    return round(raw_score, 1)





##########################################################
##########################################################
def save_story_text(analytics, slots):
    ensure_log_dir()
    sess = analytics["session_id"]
    story_text = generate_story_text(slots)
    path = os.path.join(LOG_DIR, f"{sess}_story.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("Story:\n" + story_text + "\n")
    analytics["story_quality"] = auto_story_quality(analytics, slots)
    return path
##########################################################
##########################################################

def save_session_files(analytics, slots):
    """Save CSV move log + JSON summary (includes metrics & story text)."""
    ensure_log_dir()
    sess = analytics["session_id"]

    # CSV move log
    csv_path = os.path.join(LOG_DIR, f"{sess}_moves.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        keys = sorted({k for row in analytics["move_log"] for k in row.keys()} | {"t","event"})
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for row in analytics["move_log"]:
            w.writerow(row)

    # Final mapping & story
    mapping = []
    for i, slot in enumerate(slots):
        if slot["card"]:
            mapping.append({"slot": i+1, "card_id": slot["card"].get("id"), "title": slot["card"].get("title")})
        else:
            mapping.append({"slot": i+1, "card_id": None, "title": None})
    story_text = generate_story_text(slots)

    # JSON summary
    summary = {
        "session_id": sess,
        "planning_score": compute_planning_score(analytics),
        "session_health": compute_session_health(analytics),
        "placements_manual": analytics["placements_from_deck"],
        "placements_autofill": analytics["placements_autofill"],
        "rearrangements_total": analytics["rearrangements_total"],
        "card_move_counts": analytics["card_move_counts"],
        "card_rearrangements": analytics["card_rearrangements"],
        "slot_dwell_seconds": [round(x, 3) for x in analytics["slot_dwell"]],
        "slot_view_counts": analytics["slot_views"],
        "story_quality_rating_0_10": analytics.get("story_quality"),
        "sus": {"responses_1to5": analytics.get("sus_responses"), "score_0_100": analytics.get("sus_score")},
        "nasa_tlx_raw": {"subscales_0_100": analytics.get("tlx"), "average_0_100": analytics.get("tlx_avg")},
        "final_slot_mapping": mapping,
        "story_text": story_text
    }
    json_path = os.path.join(LOG_DIR, f"{sess}_summary.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    return csv_path, json_path


#####################################33
def show_final_story_popup2(slots, analytics):
    """
    Final Story popup with ability to save story text AND give a story-quality rating (0-9).
    Saves rating into analytics['story_quality'] and shows a quick confirmation.
    """
    popup_open = True
    scroll_y = 0
    back_btn  = pygame.Rect(SCREEN_SIZE[0]//2 - 300, POPUP_BTN_Y, 180, 40)
    save_btn  = pygame.Rect(SCREEN_SIZE[0]//2 -  90, POPUP_BTN_Y, 220, 40)
    rate_dec  = pygame.Rect(SCREEN_SIZE[0]//2 + 140, POPUP_BTN_Y - 80, 44, 40)  # - button
    rate_inc  = pygame.Rect(SCREEN_SIZE[0]//2 + 220, POPUP_BTN_Y - 80, 44, 40)  # + button
    rate_box  = pygame.Rect(SCREEN_SIZE[0]//2 + 190, POPUP_BTN_Y - 80, 28, 40)

    # initialise rating if present otherwise default to 5
    if analytics.get("story_quality") is None:
        rating = 5
    else:
        try:
            rating = int(analytics.get("story_quality"))
            rating = max(0, min(9, rating))
        except:
            rating = 5

    while popup_open:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    popup_open = False
                elif event.key == pygame.K_DOWN:
                    scroll_y += 20
                elif event.key == pygame.K_UP:
                    scroll_y = max(0, scroll_y - 20)
                elif event.key == pygame.K_LEFT:
                    rating = max(0, rating - 1)
                elif event.key == pygame.K_RIGHT:
                    rating = min(9, rating + 1)
                elif event.key in (pygame.K_0, pygame.K_KP0, pygame.K_1, pygame.K_2, pygame.K_3,
                                   pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9):
                    # quick number entry 0-9
                    ch = event.key - pygame.K_0
                    if 0 <= ch <= 9:
                        rating = ch
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if event.button == 1:
                    if back_btn.collidepoint(mx, my):
                        popup_open = False
                    elif save_btn.collidepoint(mx, my):
                        path = save_story_text(analytics, slots)
                        # save rating as well
                        analytics["story_quality"] = int(rating)
                        confirm = small_font.render(f"Saved: {os.path.basename(path)}  | Rating: {rating}/9", True, (180,255,180))
                        screen.blit(confirm, (SCREEN_SIZE[0]//2 - confirm.get_width()//2, SCREEN_SIZE[1]-100))
                        pygame.display.flip(); pygame.time.delay(900)
                    elif rate_dec.collidepoint(mx, my):
                        rating = max(0, rating - 1)
                    elif rate_inc.collidepoint(mx, my):
                        rating = min(9, rating + 1)
                    elif rate_box.collidepoint(mx, my):
                        # clicking the box focuses it for keyboard number input - simple UX: do nothing special
                        pass
                elif event.button == 4:  # up
                    scroll_y = max(0, scroll_y - 20)
                elif event.button == 5:  # down
                    scroll_y += 20

        # draw overlay and content
        overlay = pygame.Surface(SCREEN_SIZE); overlay.set_alpha(220); overlay.fill((0,0,0))
        screen.blit(overlay, (0,0))

        title = big_font.render("Final Story", True, (255,255,255))
        screen.blit(title, (60, 20))

        text = generate_story_text(slots)
        maxw = SCREEN_SIZE[0] - 120
        words = text.split(); lines=[]; cur=""
        for w in words:
            test = cur + " " + w if cur else w
            if font.render(test, True, (255,255,255)).get_width() <= maxw:
                cur = test
            else:
                lines.append(cur); cur = w
        if cur: lines.append(cur)
        y = 80 - scroll_y
        for ln in lines:
            screen.blit(font.render(ln, True, (230,230,230)), (60, y)); y += 28

        # Rating UI
        label = small_font.render("Story quality (0–9):", True, (200,200,200))
        screen.blit(label, (SCREEN_SIZE[0]//2 - 260, POPUP_BTN_Y - 80 + 6))
        # draw - button, + button and rating
        pygame.draw.rect(screen, (70,70,78), rate_dec, border_radius=6)
        pygame.draw.rect(screen, (70,70,78), rate_inc, border_radius=6)
        dec_txt = font.render("-", True, (255,255,255))
        inc_txt = font.render("+", True, (255,255,255))
        screen.blit(dec_txt, (rate_dec.centerx - dec_txt.get_width()//2, rate_dec.centery - dec_txt.get_height()//2))
        screen.blit(inc_txt, (rate_inc.centerx - inc_txt.get_width()//2, rate_inc.centery - inc_txt.get_height()//2))
        # rating box
        pygame.draw.rect(screen, (40,40,48), rate_box, border_radius=6)
        rtxt = font.render(str(rating), True, (240,240,240))
        screen.blit(rtxt, (rate_box.centerx - rtxt.get_width()//2, rate_box.centery - rtxt.get_height()//2))

        draw_button(back_btn, "Back")
        draw_button(save_btn, "Save Story Text & Rating")
        pygame.display.flip()
        clock.tick(60)




#####################################33
def show_final_story_popup(slots, analytics):
    popup_open = True
    scroll_y = 0
    back_btn  = pygame.Rect(SCREEN_SIZE[0]//2 - 300, POPUP_BTN_Y, 180, 40)
    save_btn  = pygame.Rect(SCREEN_SIZE[0]//2 -  90, POPUP_BTN_Y, 180, 40)

    while popup_open:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: popup_open = False
                elif event.key == pygame.K_DOWN: scroll_y += 20
                elif event.key == pygame.K_UP:   scroll_y = max(0, scroll_y - 20)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if event.button == 1:
                    if back_btn.collidepoint(mx, my):
                        popup_open = False
                    elif save_btn.collidepoint(mx, my):
                        path = save_story_text(analytics, slots)
                        confirm = small_font.render(f"Saved: {os.path.basename(path)}", True, (180,255,180))
                        screen.blit(confirm, (SCREEN_SIZE[0]//2 - confirm.get_width()//2, SCREEN_SIZE[1]-100))
                        pygame.display.flip(); pygame.time.delay(700)
                elif event.button == 4:  # up
                    scroll_y = max(0, scroll_y - 20)
                elif event.button == 5:  # down
                    scroll_y += 20

        overlay = pygame.Surface(SCREEN_SIZE); overlay.set_alpha(220); overlay.fill((0,0,0))
        screen.blit(overlay, (0,0))

        title = big_font.render("Final Story", True, (255,255,255))
        screen.blit(title, (60, 20))

        text = generate_story_text(slots)
        maxw = SCREEN_SIZE[0] - 120
        words = text.split(); lines=[]; cur=""
        for w in words:
            test = cur + " " + w if cur else w
            if font.render(test, True, (255,255,255)).get_width() <= maxw:
                cur = test
            else:
                lines.append(cur); cur = w
        if cur: lines.append(cur)
        y = 80 - scroll_y
        for ln in lines:
            screen.blit(font.render(ln, True, (230,230,230)), (60, y)); y += 28

        draw_button(back_btn, "Back")
        draw_button(save_btn, "Save Story Text")
        pygame.display.flip()
        clock.tick(60)

#########################3
##########################
def show_analytics_popup(slots, analytics):
    popup_open = True
    left_scroll_y = 0
    back_btn = pygame.Rect(SCREEN_SIZE[0]//2 - 300, POPUP_BTN_Y, 180, 40)
    save_btn = pygame.Rect(SCREEN_SIZE[0]//2 -  90, POPUP_BTN_Y, 180, 40)
    ########################
    ###########################
    def metrics_lines():
        prof = analytics.get("profile", {}) or {}
        name  = prof.get("name")  or "-"
        age   = prof.get("age")   if prof.get("age")   is not None else "-"
        grade = prof.get("grade") if prof.get("grade") else "-"
    
        qpct = analytics.get("quiz_pct")
        qtxt = f"{qpct}%" if isinstance(qpct, (int, float)) else "not taken yet"
    
        fsc  = analytics.get("final_score")
        fsct = f"{fsc}" if isinstance(fsc, (int, float)) else "-"
    
        lines = []
        # NEW: player header
        lines.append(f"Player: {name}  |  Age: {age}  |  Grade: {grade}")
        # NEW: quiz & final score summary (Final Score = your blend from quiz & session metrics)
        lines.append(f"Quiz Score: {qtxt}  |  Final Score: {fsct}")
    
        # existing metrics (unchanged)
        lines.append(f"Planning Score: {compute_planning_score(analytics)}/100")
        lines.append(f"Session Health: {compute_session_health(analytics)}/100")
        lines.append(f"Placements (manual): {analytics['placements_from_deck']}  |  Auto-fill: {analytics['placements_autofill']}")
        lines.append(f"Rearrangements total: {analytics['rearrangements_total']}")
        avg_dwell = round(sum(analytics['slot_dwell'])/max(1, SLOTS_COLS*SLOTS_ROWS), 2)
        lines.append(f"Avg dwell/slot: {avg_dwell} s")
        lines.append(f"Story quality (0–9): {analytics.get('story_quality', 'not set')}")
        lines.append(f"SUS usability: {analytics.get('sus_score', 'not set')}")
        tlx_avg = analytics.get('tlx_avg')
        lines.append(f"NASA-TLX (raw): {tlx_avg if tlx_avg is not None else 'not set'}")
        lines.append("")  # spacer
        lines.append("Slot views (count): " + ", ".join(str(v) for v in analytics['slot_views']))
        lines.append("Slot dwell (s): " + ", ".join(str(round(v,2)) for v in analytics['slot_dwell']))
        return lines

    
    
    
    
    #########################3
    ###########################
    


    #####################################
    ####################################

    while popup_open:
        
        
        # refresh SUS/TLX from the latest saved responses each frame so Analytics shows current values
        sus_val = compute_sus(analytics.get("sus_responses"))
        if sus_val is not None:
            analytics["sus_score"] = sus_val
        tlx_val = compute_tlx_avg(analytics.get("tlx"))
        if tlx_val is not None:
            analytics["tlx_avg"] = tlx_val

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: popup_open = False
                elif event.key == pygame.K_DOWN: left_scroll_y += 20
                elif event.key == pygame.K_UP:   left_scroll_y = max(0, left_scroll_y - 20)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if back_btn.collidepoint(mx, my):
                    popup_open = False
                elif save_btn.collidepoint(mx, my):
                    csv_p, json_p = save_session_files(analytics, slots)
                    confirm = small_font.render(f"Saved: {os.path.basename(csv_p)}, {os.path.basename(json_p)}", True, (180,255,180))
                    screen.blit(confirm, (SCREEN_SIZE[0]//2 - confirm.get_width()//2, SCREEN_SIZE[1]-100))
                    pygame.display.flip(); pygame.time.delay(900)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: left_scroll_y = max(0, left_scroll_y - 20)
                elif event.button == 5: left_scroll_y += 20

        overlay = pygame.Surface(SCREEN_SIZE); overlay.set_alpha(220); overlay.fill((0,0,0))
        screen.blit(overlay, (0,0))

        title = big_font.render("Analytics", True, (255,255,180))
        screen.blit(title, (60, 20))

        block = "\n".join(metrics_lines())
        maxw = SCREEN_SIZE[0] - 120
        y = 80 - left_scroll_y
        for raw_ln in block.split("\n"):
            words = raw_ln.split()
            cur = ""
            while words:
                w = words.pop(0)
                test = cur + " " + w if cur else w
                if font.render(test, True, (255,255,255)).get_width() <= maxw:
                    cur = test
                else:
                    screen.blit(font.render(cur, True, (255,255,255)), (60, y)); y += 26
                    cur = w
            if cur != "":
                screen.blit(font.render(cur, True, (255,255,255)), (60, y)); y += 26

        draw_button(back_btn, "Back")
        draw_button(save_btn, "Save Logs")
        pygame.display.flip()
        clock.tick(60)


#############################
##############################

# === Analytics popup (metrics-only) ===


    ####################################################

   
# === Survey Popup (SUS + NASA-TLX) ===
def show_survey_popup(analytics):
    active_tab = "SUS"
    sus_idx = 0
    tlx_idx = 0
    dragging_tlx = False

    #save_btn = pygame.Rect(SCREEN_SIZE[0]//2 + 50, SCREEN_SIZE[1]-60, 180, 40)
    save_btn  = pygame.Rect(SCREEN_SIZE[0]//2 -  90, POPUP_BTN_Y, 180, 40)
    close_btn = pygame.Rect(SCREEN_SIZE[0]//2 - 230, POPUP_BTN_Y, 160, 40)
   # close_btn = pygame.Rect(SCREEN_SIZE[0]//2 - 230, SCREEN_SIZE[1]-60, 160, 40)
    
    tab_sus = pygame.Rect(60, 20, 140, 36)
    tab_tlx = pygame.Rect(210, 20, 140, 36)

    def draw_tabs():
        for tab, rect in [("SUS", tab_sus), ("TLX", tab_tlx)]:
            col = (70,140,220) if active_tab == tab else (60,60,60)
            pygame.draw.rect(screen, col, rect, border_radius=8)
            label = small_font.render(tab, True, (255,255,255))
            screen.blit(label, (rect.centerx - label.get_width()//2, rect.centery - label.get_height()//2))

    def draw_sus_and_get_boxes():
        q = SUS_ITEMS[sus_idx]
        title = big_font.render(f"SUS {sus_idx+1}/10", True, (255,255,255))
        screen.blit(title, (60, 80))
        # wrap question
        maxw = SCREEN_SIZE[0]-120
        words = q.split(); lines=[]; cur=""
        for w in words:
            test = (cur+" "+w) if cur else w
            if font.render(test, True, (255,255,255)).get_width() <= maxw:
                cur = test
            else:
                lines.append(cur); cur=w
        if cur: lines.append(cur)
        y=130
        for ln in lines:
            screen.blit(font.render(ln, True, (230,230,230)), (60,y)); y+=28

        anchors = ["Strongly\nDisagree","Disagree","Neutral","Agree","Strongly\nAgree"]
        current = analytics["sus_responses"][sus_idx]
        bx, by = 60, y+20
        bw, bh = 150, 70
        boxes = []
        for i in range(5):
            r = pygame.Rect(bx+i*(bw+12), by, bw, bh)
            boxes.append(r)
            pygame.draw.rect(screen, (80,80,80), r, border_radius=10)
            if current == i+1:
                pygame.draw.rect(screen, (90,190,110), r, width=4, border_radius=10)
            num = big_font.render(str(i+1), True, (255,255,255))
            screen.blit(num, (r.centerx - num.get_width()//2, r.y+6))
            for j, line in enumerate(anchors[i].split("\n")):
                t = small_font.render(line, True, (220,220,220))
                screen.blit(t, (r.centerx - t.get_width()//2, r.y+34+18*j))
        hint = small_font.render("↑/↓ change item • 1–5 to answer • Enter=next • Tab=NASA-TLX", True, (200,200,200))
        screen.blit(hint, (60, SCREEN_SIZE[1]-100))
        return boxes

    def draw_tlx_and_get_tracks():
        title = big_font.render("NASA-TLX (Raw)", True, (255,255,255))
        screen.blit(title, (60, 80))
        hint = small_font.render("↑/↓ select scale • ←/→ adjust • Click/drag slider • Tab=SUS", True, (200,200,200))
        screen.blit(hint, (60, 120))

        base_y = 160
        track_w = SCREEN_SIZE[0]-160
        tracks = []
        for i, key in enumerate(TLX_KEYS):
            y = base_y + i*70
            sel = (i == tlx_idx)
            label = font.render(f"{key}", True, (255,255,200) if sel else (220,220,220))
            screen.blit(label, (60, y-6))
            track = pygame.Rect(260, y, track_w-260, 10)
            pygame.draw.rect(screen, (90,90,90), track, border_radius=5)
            val = analytics["tlx"][key]
            hx = track.x + int(val/100 * track.width)
            handle = pygame.Rect(hx-8, track.y-8, 16, 26)
            pygame.draw.rect(screen, (200,200,200), handle, border_radius=6)
            for tval in [0,50,100]:
                tx = track.x + int(tval/100*track.width)
                pygame.draw.line(screen, (130,130,130), (tx, track.y-6), (tx, track.y+16), 2)
                tlabel = small_font.render(str(tval), True, (180,180,180))
                screen.blit(tlabel, (tx-10, track.y+22))
            left = "Low" if key!="Performance" else "Good"
            right = "High" if key!="Performance" else "Poor"
            screen.blit(small_font.render(left, True, (180,180,220)), (track.x, track.y-24))
            tr = small_font.render(right, True, (220,180,180))
            screen.blit(tr, (track.right - tr.get_width(), track.y-24))
            tracks.append((i, key, track))
        avg = compute_tlx_avg(analytics["tlx"])
        if avg is not None:
            avg_s = small_font.render(f"RAW TLX average: {avg}/100", True, (200,230,255))
            screen.blit(avg_s, (60, SCREEN_SIZE[1]-100))
        return tracks

    running=True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running=False
                elif event.key == pygame.K_TAB: active_tab = "TLX" if active_tab=="SUS" else "SUS"
                elif active_tab=="SUS":
                    if event.key == pygame.K_UP:   sus_idx = (sus_idx-1) % 10
                    elif event.key in (pygame.K_DOWN, pygame.K_RETURN): sus_idx = (sus_idx+1) % 10
                    elif pygame.K_1 <= event.key <= pygame.K_5:
                        analytics["sus_responses"][sus_idx] = event.key - pygame.K_0
                else:
                    if event.key == pygame.K_UP:   tlx_idx = (tlx_idx-1) % len(TLX_KEYS)
                    elif event.key == pygame.K_DOWN: tlx_idx = (tlx_idx+1) % len(TLX_KEYS)
                    elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        key = TLX_KEYS[tlx_idx]; delta = -5 if event.key==pygame.K_LEFT else 5
                        analytics["tlx"][key] = max(0, min(100, analytics["tlx"][key] + delta))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if event.button == 1:
                    if close_btn.collidepoint(mx,my): running=False
                    elif save_btn.collidepoint(mx,my):
                        analytics["sus_score"] = compute_sus(analytics["sus_responses"])
                        analytics["tlx_avg"] = compute_tlx_avg(analytics["tlx"])
                        log_event(analytics, "survey_saved", sus_score=analytics["sus_score"], tlx_avg=analytics["tlx_avg"])
                        running=False
                    if tab_sus.collidepoint(mx,my): active_tab="SUS"
                    if tab_tlx.collidepoint(mx,my): active_tab="TLX"
                    if active_tab=="SUS":
                        # rebuild boxes to hit-test
                        overlay = pygame.Surface(SCREEN_SIZE); overlay.set_alpha(0); screen.blit(overlay,(0,0))
                        boxes = draw_sus_and_get_boxes()
                        for i, r in enumerate(boxes, start=1):
                            if r.collidepoint(mx,my): analytics["sus_responses"][sus_idx] = i; break
                    else:
                        tracks = draw_tlx_and_get_tracks()
                        for i, key, track in tracks:
                            if track.collidepoint(mx,my):
                                analytics["tlx"][key] = int(round((mx - track.x)/track.width * 100))
                                tlx_idx = i; dragging_tlx=True; break
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_tlx = False
            elif event.type == pygame.MOUSEMOTION and dragging_tlx and active_tab=="TLX":
                mx, my = event.pos
                base_y = 160; track_w = SCREEN_SIZE[0]-160
                key = TLX_KEYS[tlx_idx]
                y = base_y + tlx_idx*70
                track = pygame.Rect(260, y, track_w-260, 10)
                analytics["tlx"][key] = int(round(max(0, min(1, (mx-track.x)/track.width)) * 100))

        # overlay
        overlay = pygame.Surface(SCREEN_SIZE); overlay.set_alpha(230); overlay.fill((0,0,0))
        screen.blit(overlay,(0,0))
        draw_tabs()
        # draw active panel
        if active_tab=="SUS": draw_sus_and_get_boxes()
        else: draw_tlx_and_get_tracks()

        # buttons
        draw_button(close_btn, "Back")
        draw_button(save_btn, "Save Ratings")
        pygame.display.flip()
        clock.tick(60)
##############################3333
# === QUIZ: 20 MCQs from the Pebble story ===
# Game will randomly pick 10 each run
QUIZ_FINAL_BLEND = (0.60, 0.40)  # (weight_session_health, weight_quiz_pct)

DEFAULT_20_MCQ = [
    {"qid":"q1", "text":"Why was the farmer in trouble?", 
     "options":["He lost his land","He owed money","He broke a law","He was ill"], "answer":1},
    {"qid":"q2", "text":"What did the moneylender propose in exchange for cancelling the debt?",
     "options":["Sell the farm","Marry the daughter","Work for him","Leave the village"], "answer":1},
    {"qid":"q3", "text":"How did the farmer and his daughter feel about the proposal?",
     "options":["Delighted","Indifferent","Horrified","Confused"], "answer":2},
    {"qid":"q4", "text":"What method of decision did the moneylender suggest?",
     "options":["A coin toss","A village vote","Drawing a pebble from a bag","Asking the priest"], "answer":2},
    {"qid":"q5", "text":"Which two colors were supposed to be in the bag?",
     "options":["Black & red","White & red","Black & white","White & green"], "answer":2},
    {"qid":"q6", "text":"What did the moneylender actually put in the bag?",
     "options":["Two white pebbles","Two black pebbles","One black, one white","No pebbles"], "answer":1},
    {"qid":"q7", "text":"Where were they standing when this happened?",
     "options":["In the market","By the river","On a pebble-strewn path in the farmer’s field","Inside the moneylender’s house"], "answer":2},
    {"qid":"q8", "text":"If the girl drew a black pebble (per the rules), what would happen?",
     "options":["She could leave","She must marry the moneylender and the debt is cancelled","Her father goes to jail","Nothing changes"], "answer":1},
    {"qid":"q9", "text":"If the girl drew a white pebble (per the rules), what would happen?",
     "options":["She must marry him","Debt remains","Debt is cancelled and she need not marry","She must leave the village"], "answer":2},
    {"qid":"q10", "text":"If the girl refused to pick a pebble, what was the threat?",
     "options":["Lose the farm","Public shaming","Father jailed","Exile"], "answer":2},
    {"qid":"q11", "text":"What did the girl actually do with the pebble she drew?",
     "options":["Hid it","Put it back","Dropped it “by accident” so it was lost","Showed it immediately"], "answer":2},
    {"qid":"q12", "text":"Why did dropping the pebble help?",
     "options":["It bought time","It made the choice invalid","The remaining pebble reveals what she must have picked","It scared the moneylender"], "answer":2},
    {"qid":"q13", "text":"Why couldn’t the moneylender admit the truth after the drop?",
     "options":["He forgot","He’d reveal his cheating","He feared the farmer","He lost his ledger"], "answer":1},
    {"qid":"q14", "text":"What key lesson does the story emphasize?",
     "options":["Follow tradition","Ask elders","Think laterally / out of the box","Rely on luck"], "answer":2},
    {"qid":"q15", "text":"Which option was NOT among the three “logical” possibilities listed?",
     "options":["Refuse to pick a pebble","Expose the two black pebbles","Pick a black pebble to save father","Ask the village head to arbitrate"], "answer":3},
    {"qid":"q16", "text":"Which best describes the girl’s strategy?",
     "options":["Brute force","Minimal evidence to force inference","Appeal to authority","Random chance"], "answer":1},
    {"qid":"q17", "text":"Why didn’t the girl look at the pebble after drawing it?",
     "options":["She was scared","To prevent the cheat from trapping her; the unknown lets the remaining pebble prove the result","She forgot","Custom forbids it"], "answer":1},
    {"qid":"q18", "text":"Who noticed the moneylender’s cheating?",
     "options":["The farmer","The villagers","The daughter","Nobody"], "answer":2},
    {"qid":"q19", "text":"What did the moneylender mean by “let providence decide”?",
     "options":["Ask the priest","Let chance seem to decide","Go to court","Consult the stars"], "answer":1},
    {"qid":"q20", "text":"What best captures “lateral thinking” in this story?",
     "options":["Memorizing rules","Strict logic only","Creative reframing to turn constraints into an advantage","Ignoring the problem"], "answer":2},
]

def pick_quiz_10():
    import random
    return random.sample(DEFAULT_20_MCQ, 10)

def compute_quiz_pct(answers):
    # answers: list of tuples [(qid, chosen_index, correct_index), ...] length 10
    if not answers:
        return 0.0
    correct = sum(1 for (_, chosen, correct) in answers if chosen == correct)
    return round(100.0 * correct / len(answers), 2)

def append_results_row_csv(analytics, slots, quiz_pct, final_score, path="logs/results_master.csv"):
    ensure_log_dir()
    import csv, time
    headers = [
        "session_id","timestamp",
        "name","age","grade",
        "planning_score","sus_score","tlx_avg","session_health",
        "quiz_pct","final_score",
        "placements_manual","rearrangements_total",
        "avg_dwell_per_slot","total_dwell_seconds",
        "story_text"
    ]
    prof = analytics.get("profile", {}) or {}
    planning = compute_planning_score(analytics)
    sus = analytics.get("sus_score")
    tlx = analytics.get("tlx_avg")
    session_health = compute_session_health(analytics)
    avg_dwell = round(sum(analytics["slot_dwell"]) / max(1, len(analytics["slot_dwell"])), 3)
    total_dwell = round(sum(analytics["slot_dwell"]), 3)
    story_text = generate_story_text(slots)

    row = {
        "session_id": analytics.get("session_id"),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "name": prof.get("name"), "age": prof.get("age"), "grade": prof.get("grade"),
        "planning_score": planning, "sus_score": sus, "tlx_avg": tlx, "session_health": session_health,
        "quiz_pct": quiz_pct, "final_score": final_score,
        "placements_manual": analytics.get("placements_from_deck"),
        "rearrangements_total": analytics.get("rearrangements_total"),
        "avg_dwell_per_slot": avg_dwell, "total_dwell_seconds": total_dwell,
        "story_text": story_text
    }

    new_file = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        if new_file:
            w.writeheader()
        w.writerow(row)
#####################################################3
# === Text wrap helper (for quiz/questions etc.) ===
def wrap_text(text, fnt, max_width):
    """
    Split `text` into lines that fit within `max_width` pixels when rendered with font `fnt`.
    Returns a list of lines (strings).
    """
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = f"{line} {w}" if line else w
        if fnt.render(test, True, (0, 0, 0)).get_width() <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines

#############################################################
def quiz_popup_and_score(analytics):
    """
    Shows 10 MCQs (single-choice) sampled from DEFAULT_20_MCQ.
    Returns (quiz_pct, final_score) on Submit, or (None, None) if Back.
    """
    questions = pick_quiz_10()
    idx = 0
    chosen = {q["qid"]: None for q in questions}

    back_btn   = pygame.Rect(60,  SCREEN_SIZE[1]-70, 120, 44)
    prev_btn   = pygame.Rect(190, SCREEN_SIZE[1]-70, 120, 44)
    next_btn   = pygame.Rect(320, SCREEN_SIZE[1]-70, 120, 44)
    submit_btn = pygame.Rect(SCREEN_SIZE[0]-220, SCREEN_SIZE[1]-70, 160, 44)

    running = True
    while running:
        click_pos = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None, None  # Back
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    idx = min(9, idx + 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    idx = max(0, idx - 1)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    # Submit via Enter
                    triplets = []
                    for qq in questions:
                        sel = chosen[qq["qid"]]
                        if sel is None: sel = -1
                        triplets.append((qq["qid"], sel, qq["answer"]))
                    quiz_pct = compute_quiz_pct(triplets)
                    w_s, w_q = QUIZ_FINAL_BLEND
                    final_score = round(w_s * compute_session_health(analytics) + w_q * quiz_pct, 2)
                    return quiz_pct, final_score
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click_pos = event.pos

        screen.fill((18,18,28))
        screen.blit(big_font.render("Quiz", True, (255,255,180)), (60, 20))
        screen.blit(small_font.render(f"Question {idx+1}/10", True, (200,200,200)), (60, 60))

        q = questions[idx]
        y = 110
        for ln in wrap_text(q["text"], font, SCREEN_SIZE[0]-120):
            screen.blit(font.render(ln, True, (230,230,230)), (60, y)); y += 28

        boxes = []
        for i, opt in enumerate(q["options"]):
            r = pygame.Rect(80, y + i*46, SCREEN_SIZE[0]-160, 36)
            boxes.append((i, r))
            pygame.draw.rect(screen, (60,60,70), r, border_radius=6)
            active = (chosen[q["qid"]] == i)
            pygame.draw.rect(screen, (100,200,120) if active else (110,110,110), r, 2, border_radius=6)
            screen.blit(small_font.render(opt, True, (230,230,230)), (r.x+10, r.y+8))

        draw_button(back_btn, "Back")
        draw_button(prev_btn, "Previous")
        draw_button(next_btn, "Next")
        draw_button(submit_btn, "Submit")

        if click_pos:
            mx, my = click_pos
            if back_btn.collidepoint((mx,my)):
                return None, None
            elif prev_btn.collidepoint((mx,my)):
                idx = max(0, idx - 1)
            elif next_btn.collidepoint((mx,my)):
                idx = min(9, idx + 1)
            elif submit_btn.collidepoint((mx,my)):
                triplets = []
                for qq in questions:
                    sel = chosen[qq["qid"]]
                    if sel is None: sel = -1
                    triplets.append((qq["qid"], sel, qq["answer"]))
                quiz_pct = compute_quiz_pct(triplets)
                w_s, w_q = QUIZ_FINAL_BLEND
                final_score = round(w_s * compute_session_health(analytics) + w_q * quiz_pct, 2)
                return quiz_pct, final_score
            else:
                for i, r in boxes:
                    if r.collidepoint((mx,my)):
                        chosen[q["qid"]] = i
                        break

        pygame.display.flip()
        clock.tick(60)





#######################################3
# === Auto-Fill helper ===
def auto_fill_empty_slots(slots, deck, analytics):
    """Randomly fills empty slots from the deck (does not disturb filled slots)."""
    empty_idxs = [i for i, s in enumerate(slots) if s["card"] is None]
    if not empty_idxs or not deck: return 0
    random.shuffle(empty_idxs); random.shuffle(deck)
    log_event(analytics, "auto_fill_start", empties=len(empty_idxs), deck_before=len(deck))
    placed = 0
    for idx in empty_idxs:
        if not deck: break
        card = deck.pop()
        slots[idx]["card"] = card
        analytics["placements_autofill"] += 1
        analytics["card_move_counts"][card["id"]] += 1
        placed += 1
        log_event(analytics, "auto_fill_place", dst=f"slot_{idx+1}", card_id=card["id"], title=card["title"], deck_after=len(deck))
    log_event(analytics, "auto_fill_end", placed=placed, deck_after=len(deck))
    return placed
#########################################3
############################################
# === Simple text input for profile ===
class TextInput:
    def __init__(self, rect, placeholder="", only_digits=False, max_len=32):
        self.rect = pygame.Rect(rect)
        self.placeholder = placeholder
        self.only_digits = only_digits
        self.max_len = max_len
        self.value = ""
        self.focus = False

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.focus = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.focus:
            if event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            elif event.key == pygame.K_RETURN:
                self.focus = False
            else:
                ch = event.unicode
                if len(ch) != 1:
                    return
                if self.only_digits and not ch.isdigit():
                    return
                if 32 <= ord(ch) <= 126 and len(self.value) < self.max_len:
                    self.value += ch

    def draw(self):
        # box
        pygame.draw.rect(screen, (70,70,78), self.rect, border_radius=8)
        pygame.draw.rect(screen, (120,120,130) if self.focus else (90,90,96),
                         self.rect, 2, border_radius=8)
        # text
        txt = self.value if self.value else self.placeholder
        col = (255,255,255) if self.value else (170,170,170)
        surf = font.render(txt, True, col)
        screen.blit(surf, (self.rect.x+10, self.rect.y + (self.rect.height - surf.get_height())//2))
######################3
######################3
##########################3

def resource_path1(relative_path):
    """ Get absolute path to resource, works for dev & PyInstaller """
    try:
        base_path = sys._MEIPASS  # When running in exe
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def show_profile_popup():
    """
    Blocks until user enters Name (required), Age (required digits), Grade (optional).
    Returns (name:str, age:int, grade:str or None).
    """
    overlay_bg = (20,20,28)
    title = big_font.render("Enter Player Details", True, (255,255,180))

    # Load logo (bundled in exe)
    try:
        logo_path = resource_path1("logo1.png")
        logo = pygame.image.load(logo_path)
        logo = pygame.transform.scale(logo, (220, 120))  # resize
    except Exception as e:
        logo = None
        print("Logo not found:", e)

    # layout
    box_w, box_h = 360, 44
    label_x = SCREEN_SIZE[0]//2 - 260     # left side for labels
    box_x   = SCREEN_SIZE[0]//2 - box_w//2 + 80  # right side for input boxes
    y0 = 280   # shifted down to make space for logo

    # inputs
    name_in  = TextInput((box_x, y0 + 0*70,  box_w, box_h), "Name (required)")
    age_in   = TextInput((box_x, y0 + 1*70,  box_w, box_h), "Age (required)", only_digits=True, max_len=3)
    grade_in = TextInput((box_x, y0 + 2*70,  box_w, box_h), "Grade (optional)")
    start_btn = pygame.Rect(box_x + 60, y0 + 3*70 + 24, 200, 46)

    # set initial focus to name
    name_in.focus = True
    error_msg = ""

    def valid():
        if not name_in.value.strip():
            return False, "Please enter a name."
        if not age_in.value.isdigit():
            return False, "Please enter a valid age (digits only)."
        age = int(age_in.value)
        if not (4 <= age <= 99):
            return False, "Age must be between 4 and 99."
        return True, ""

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

            # inputs
            name_in.handle(event)
            age_in.handle(event)
            grade_in.handle(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if start_btn.collidepoint(mx, my):
                    ok, msg = valid()
                    if ok:
                        grade_val = grade_in.value.strip() or None
                        return name_in.value.strip(), int(age_in.value), grade_val
                    else:
                        error_msg = msg

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if name_in.focus:
                    name_in.focus = False; age_in.focus = True
                elif age_in.focus:
                    age_in.focus = False; grade_in.focus = True
                else:
                    ok, msg = valid()
                    if ok:
                        grade_val = grade_in.value.strip() or None
                        return name_in.value.strip(), int(age_in.value), grade_val
                    else:
                        error_msg = msg

        # draw popup
        screen.fill(overlay_bg)

        # draw logo if available
        if logo:
            screen.blit(logo, (SCREEN_SIZE[0]//2 - logo.get_width()//2, 60))

        # draw title
        screen.blit(title, (SCREEN_SIZE[0]//2 - title.get_width()//2, 200))

        # labels with spacing before boxes
        screen.blit(small_font.render("Name:",  True, (210,210,220)), (label_x, y0 + 0*70 + 10))
        screen.blit(small_font.render("Age:",   True, (210,210,220)), (label_x, y0 + 1*70 + 10))
        screen.blit(small_font.render("Grade:", True, (210,210,220)), (label_x, y0 + 2*70 + 10))

        # fields
        name_in.draw()
        age_in.draw()
        grade_in.draw()

        # button
        ok, _ = valid()
        draw_button(start_btn, "Start", enabled=ok)

        # error message
        if error_msg:
            err = small_font.render(error_msg, True, (255,200,200))
            screen.blit(err, (SCREEN_SIZE[0]//2 - err.get_width()//2, start_btn.bottom + 12))

        pygame.display.flip()
        clock.tick(60)













###################33

def show_profile_popup1():
    """
    Blocks until user enters Name (required), Age (required digits), Grade (optional).
    Returns (name:str, age:int, grade:str or None).
    """
    overlay_bg = (20,20,28)
    title = big_font.render("Enter Player Details", True, (255,255,180))

    # layout
    box_w, box_h = 360, 44
    label_x = SCREEN_SIZE[0]//2 - 260     # left side for labels
    box_x   = SCREEN_SIZE[0]//2 - box_w//2 + 80  # right side for input boxes
    y0 = 240

    # inputs
    name_in  = TextInput((box_x, y0 + 0*70,  box_w, box_h), "Name (required)")
    age_in   = TextInput((box_x, y0 + 1*70,  box_w, box_h), "Age (required)", only_digits=True, max_len=3)
    grade_in = TextInput((box_x, y0 + 2*70,  box_w, box_h), "Grade (optional)")
    start_btn = pygame.Rect(box_x + 60, y0 + 3*70 + 24, 200, 46)

    # set initial focus to name
    name_in.focus = True

    error_msg = ""

    def valid():
        if not name_in.value.strip():
            return False, "Please enter a name."
        if not age_in.value.isdigit():
            return False, "Please enter a valid age (digits only)."
        age = int(age_in.value)
        if not (4 <= age <= 99):
            return False, "Age must be between 4 and 99."
        return True, ""

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

            # inputs
            name_in.handle(event)
            age_in.handle(event)
            grade_in.handle(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if start_btn.collidepoint(mx, my):
                    ok, msg = valid()
                    if ok:
                        grade_val = grade_in.value.strip() or None
                        return name_in.value.strip(), int(age_in.value), grade_val
                    else:
                        error_msg = msg

            # quick Enter-to-advance UX
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if name_in.focus:
                    name_in.focus = False; age_in.focus = True
                elif age_in.focus:
                    age_in.focus = False; grade_in.focus = True
                else:
                    ok, msg = valid()
                    if ok:
                        grade_val = grade_in.value.strip() or None
                        return name_in.value.strip(), int(age_in.value), grade_val
                    else:
                        error_msg = msg

        # draw popup
        screen.fill(overlay_bg)
        screen.blit(title, (SCREEN_SIZE[0]//2 - title.get_width()//2, 160))

        # labels with spacing before boxes
        screen.blit(small_font.render("Name:",  True, (210,210,220)), (label_x, y0 + 0*70 + 10))
        screen.blit(small_font.render("Age:",   True, (210,210,220)), (label_x, y0 + 1*70 + 10))
        screen.blit(small_font.render("Grade:", True, (210,210,220)), (label_x, y0 + 2*70 + 10))

        # fields
        name_in.draw()
        age_in.draw()
        grade_in.draw()

        # button
        ok, _ = valid()
        draw_button(start_btn, "Start", enabled=ok)

        # error message
        if error_msg:
            err = small_font.render(error_msg, True, (255,200,200))
            screen.blit(err, (SCREEN_SIZE[0]//2 - err.get_width()//2, start_btn.bottom + 12))

        pygame.display.flip()
        clock.tick(60)








#################################################33
def show_intro_popup(analytics):
    """
    Displays a short story introduction with Continue & Skip buttons.
    Blocks until player clicks Continue or Skip.
    Records time spent and skip status in analytics.
    """
    intro_text = (
        "• A farmer owed a large debt to a cunning moneylender.\n"
        "• The moneylender wanted to marry the farmer’s daughter in exchange for clearing the debt.\n"
        "• To decide, he suggested a pebble game: one black pebble and one white pebble in a bag.\n"
        "• Secretly, he put two black pebbles in the bag to cheat.\n"
        "• The daughter noticed, then cleverly dropped her chosen pebble on the ground.\n"
        "• By showing the remaining pebble was black, everyone assumed she had picked white — debt cleared, no marriage.\n\n"
        "Lesson: Even impossible problems can have smart, creative solutions if we think out of the box."
    )

    popup_open = True
    scroll_y = 0
    cont_btn = pygame.Rect(SCREEN_SIZE[0]//2 - 200, SCREEN_SIZE[1]-80, 180, 46)
    skip_btn = pygame.Rect(SCREEN_SIZE[0]//2 + 20, SCREEN_SIZE[1]-80, 180, 46)

    start_time = time.perf_counter()
    skipped = False

    while popup_open:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                elif event.key == pygame.K_DOWN:
                    scroll_y += 20
                elif event.key == pygame.K_UP:
                    scroll_y = max(0, scroll_y - 20)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if event.button == 1:
                    if cont_btn.collidepoint(mx, my):
                        skipped = False
                        popup_open = False
                    elif skip_btn.collidepoint(mx, my):
                        skipped = True
                        popup_open = False
                elif event.button == 4:  # scroll up
                    scroll_y = max(0, scroll_y - 20)
                elif event.button == 5:  # scroll down
                    scroll_y += 20

        # background
        screen.fill((20,20,28))

        # title
        title = big_font.render("Story Introduction", True, (255, 255, 180))
        screen.blit(title, (SCREEN_SIZE[0]//2 - title.get_width()//2, 50))

        # text wrapping
        maxw = SCREEN_SIZE[0] - 160
        lines = []
        for ln in intro_text.split("\n"):
            words = ln.split()
            cur = ""
            for w in words:
                test = cur + " " + w if cur else w
                if font.render(test, True, (230,230,230)).get_width() <= maxw:
                    cur = test
                else:
                    lines.append(cur)
                    cur = w
            if cur:
                lines.append(cur)
            lines.append("")

        y = 140 - scroll_y
        for ln in lines:
            screen.blit(font.render(ln, True, (230,230,230)), (80, y))
            y += 28

        # buttons
        draw_button(cont_btn, "Continue")
        draw_button(skip_btn, "Skip Intro")

        pygame.display.flip()
        clock.tick(60)

    elapsed = time.perf_counter() - start_time
    analytics["intro_time_seconds"] = round(elapsed, 2)
    analytics["intro_skipped"] = skipped






######################################################
# === MAIN ===
def main():
    show_splash_screen()   # splash screen first
    deck = load_cards(CARD_FOLDER)
    slots = create_slots()

    # --- Analytics state ---
   
    analytics = {
    "session_id": time.strftime("%Y%m%d_%H%M%S"),
    "t0": time.perf_counter(),
    "move_log": [],
    "card_move_counts": defaultdict(int),
    "card_rearrangements": defaultdict(int),
    "placements_from_deck": 0,
    "placements_autofill": 0,
    "rearrangements_total": 0,
    "slot_dwell": [0.0 for _ in range(len(slots))],
    "slot_views": [0 for _ in range(len(slots))],
    "hover_idx": None,
    "story_quality": None,
    "show_heatmap": False,
    # SUS/TLX state
    "sus_responses": [None]*10,
    "sus_score": None,
    "tlx": {k: 50 for k in TLX_KEYS},
    "tlx_avg": None,
    "quiz_pct": None,
    "final_score": None,
    # NEW: profile
    "profile": {"name": None, "age": None, "grade": None}
    
    }
    
    
    
    
    dragging_card = None
    dragging_from_slot = None
    offset_x, offset_y = 0, 0

    # Buttons (left → right)
   
    
    evaluate_btn = pygame.Rect(SCREEN_SIZE[0] - 1180, BUTTON_BAR_Y, 180, 40)
    autofill_btn  = pygame.Rect(SCREEN_SIZE[0] -  980, BUTTON_BAR_Y, 180, 40)
    reset_btn     = pygame.Rect(SCREEN_SIZE[0] -  780, BUTTON_BAR_Y, 180, 40)
    shuffle_btn   = pygame.Rect(SCREEN_SIZE[0] -  580, BUTTON_BAR_Y, 180, 40)
    story_btn     = pygame.Rect(SCREEN_SIZE[0] -  380, BUTTON_BAR_Y, 180, 40)
    analytics_btn = pygame.Rect(SCREEN_SIZE[0] -  180, BUTTON_BAR_Y, 180, 40)
    
    finish_quiz_btn = pygame.Rect(SCREEN_SIZE[0] -  1180, BUTTON_BAR_Y - 50, 180, 40)

    ensure_log_dir()
    status_msg = ""; status_ttl = 0.0
    #############################################3
    ###############################################3
    
   
    # --- Ask for profile before starting the game ---
    name, age, grade = show_profile_popup()
    analytics["profile"] = {"name": name, "age": age, "grade": grade}
    log_event(analytics, "profile_saved", name=name, age=age, grade=grade)
     
    show_intro_popup(analytics)

    
    
    ######################################################3
    #########################################################3


















    while True:
        dt = clock.get_time() / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h: analytics["show_heatmap"] = not analytics["show_heatmap"]

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                if evaluate_btn.collidepoint(mx, my):
                    show_survey_popup(analytics)
                    status_msg = "SUS/TLX saved (if completed)."; status_ttl = 1.4

                elif autofill_btn.collidepoint(mx, my):
                    placed = auto_fill_empty_slots(slots, deck, analytics)
                    status_msg = (f"Auto-filled {placed} empty slot(s)." if placed > 0 else "Nothing to auto-fill.")
                    status_ttl = 2.0

                elif reset_btn.collidepoint(mx, my):
                    cleared = 0
                    for i, slot in enumerate(slots):
                        if slot["card"]:
                            deck.append(slot["card"])
                            log_event(analytics, "return_all_to_deck", slot=i+1, card_id=slot["card"]["id"], title=slot["card"]["title"])
                            slot["card"] = None; cleared += 1
                    random.shuffle(deck)
                    analytics.update({
                        "session_id": time.strftime("%Y%m%d_%H%M%S"),
                        "t0": time.perf_counter(),
                        "move_log": [],
                        "card_move_counts": defaultdict(int),
                        "card_rearrangements": defaultdict(int),
                        "placements_from_deck": 0,
                        "placements_autofill": 0,
                        "rearrangements_total": 0,
                        "slot_dwell": [0.0 for _ in range(len(slots))],
                        "slot_views": [0 for _ in range(len(slots))],
                        "hover_idx": None,
                        "story_quality": None,
                        "sus_responses": [None]*10,
                        "sus_score": None,
                        "tlx_avg": None,
                        "quiz_pct": None,
                        "final_score": None,
                        "tlx": {k: 50 for k in TLX_KEYS},
                        
                    })
                    log_event(analytics, "reset_all", deck_after=len(deck))
                    status_msg = f"Reset done. Cleared {cleared} slot(s)."; status_ttl = 1.5

                elif shuffle_btn.collidepoint(mx, my):
                    random.shuffle(deck)
                    log_event(analytics, "shuffle", deck_after=len(deck))
                    status_msg = "Deck shuffled."; status_ttl = 1.2

                elif story_btn.collidepoint(mx, my):
                    show_final_story_popup(slots, analytics)

                elif analytics_btn.collidepoint(mx, my):
                    show_analytics_popup(slots, analytics)
                ###################################################
                elif finish_quiz_btn.collidepoint(mx, my):
                    # Only allow if all slots filled
                            
                    all_placed = (len(deck) == 0)
                    if not all_placed:
                        placed_count = sum(1 for s in slots if s["card"])
                        status_msg = f"Place all cards first ({placed_count} placed)"
                        status_ttl = 2.0
                    else:
                        quiz_pct, final_score = quiz_popup_and_score(analytics)
                        if quiz_pct is None:
                            status_msg = "Quiz cancelled."
                            status_ttl = 1.4
                        else:
                            # NEW: store for analytics popup
                            analytics["quiz_pct"] = quiz_pct
                            analytics["final_score"] = final_score
                    
                            # existing: append to results CSV
                            append_results_row_csv(analytics, slots, quiz_pct, final_score)
                    
                            status_msg = f"Quiz saved. Final Score: {final_score}"
                            status_ttl = 2.4 
                                           ##########################################################     
                else:
                    # Deck drag start
                    if deck:
                        rect = pygame.Rect(DECK_POS[0], DECK_POS[1], CARD_SIZE[0], CARD_SIZE[1])
                        if rect.collidepoint(mx, my):
                            dragging_card = deck[-1]
                            offset_x = mx - rect.x; offset_y = my - rect.y
                            dragging_from_slot = None
                            log_event(analytics, "grab", src="deck", card_id=dragging_card["id"], title=dragging_card["title"], deck_before=len(deck))
                    # Slot drag start
                    if dragging_card is None:
                        for i, slot in enumerate(slots):
                            if slot["card"] and slot["rect"].collidepoint(mx, my):
                                dragging_card = slot["card"]
                                offset_x = mx - slot["rect"].x; offset_y = my - slot["rect"].y
                                dragging_from_slot = i
                                log_event(analytics, "grab", src=f"slot_{i+1}", card_id=dragging_card["id"], title=dragging_card["title"])
                                break

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragging_card:
                mx, my = event.pos
                placed = False
                card_id = dragging_card["id"]; ttl = dragging_card["title"]

                # Return to deck?
                deck_rect = pygame.Rect(DECK_POS[0], DECK_POS[1], CARD_SIZE[0], CARD_SIZE[1])
                if deck_rect.collidepoint(mx, my) and dragging_from_slot is not None:
                    deck.insert(0, dragging_card)
                    slots[dragging_from_slot]["card"] = None
                    log_event(analytics, "return_to_deck", src=f"slot_{dragging_from_slot+1}", dst="deck", card_id=card_id, title=ttl, deck_after=len(deck))
                    placed = True

                # Drop on slot?
                if not placed:
                    for i, slot in enumerate(slots):
                        if slot["rect"].collidepoint(mx, my):
                            if dragging_from_slot is None:  # from deck
                                if slot["card"]:
                                    old = slot["card"]; deck.insert(0, old)
                                    log_event(analytics, "replace_slot", dst=f"slot_{i+1}", replaced_card_id=old["id"], replaced_title=old["title"])
                                slot["card"] = deck.pop()
                                analytics["placements_from_deck"] += 1
                                analytics["card_move_counts"][card_id] += 1
                                log_event(analytics, "place_from_deck", dst=f"slot_{i+1}", card_id=card_id, title=ttl, deck_after=len(deck))
                            else:  # slot→slot
                                if i != dragging_from_slot:
                                    src_card = slots[dragging_from_slot]["card"]
                                    dst_card = slots[i]["card"]
                                    slots[dragging_from_slot]["card"], slots[i]["card"] = dst_card, src_card
                                    analytics["rearrangements_total"] += 1
                                    analytics["card_rearrangements"][src_card["id"]] += 1
                                    if dst_card:
                                        analytics["card_rearrangements"][dst_card["id"]] += 1
                                    log_event(analytics, "rearrange", src=f"slot_{dragging_from_slot+1}", dst=f"slot_{i+1}",
                                              card_id=src_card["id"], title=src_card["title"], swapped_with=(dst_card["id"] if dst_card else None))
                            placed = True
                            break
                dragging_card = None; dragging_from_slot = None

        # dwell update
        mx, my = pygame.mouse.get_pos()
        hover_idx = hovered_slot_index(slots, mx, my)
        update_dwell(analytics, hover_idx, dt)

        # status TTL
        if status_ttl > 0: status_ttl = max(0.0, status_ttl - dt)

        # Draw
        screen.fill((30, 30, 40))
        draw_slots(slots, dragging_card)
        if analytics["show_heatmap"]: draw_heatmap(slots, analytics)
        draw_deck(deck, dragging_card)

        # Buttons row
        draw_button(evaluate_btn, "Evaluate (SUS/TLX)")
        draw_button(autofill_btn,  "Auto-Fill Empty")
        draw_button(reset_btn,     "Reset All")
        draw_button(shuffle_btn,   "Shuffle Deck")
        draw_button(story_btn,     "Show Final Story")
        draw_button(analytics_btn, "Analytics")
        #all_full = all(s["card"] for s in slots)
        all_placed = (len(deck) == 0)
        draw_button(
        finish_quiz_btn,
        "Finish & Quiz",
        enabled=all_placed if 'enabled' in draw_button.__code__.co_varnames else True
        )
        # HUD
        hud = small_font.render(
            f"Planning: {compute_planning_score(analytics)}  |  Session Health: {compute_session_health(analytics)}  (H=Heatmap)",
            True, (200, 230, 255)
        )
        screen.blit(hud, (20, SCREEN_SIZE[1]-30))

        # Status toast
        if status_ttl > 0 and status_msg:
            msg_surf = small_font.render(status_msg, True, (255, 255, 200))
            bg = pygame.Surface((msg_surf.get_width()+14, msg_surf.get_height()+10))
            bg.set_alpha(160); bg.fill((20, 20, 20))
            screen.blit(bg, (20, SCREEN_SIZE[1]-60))
            screen.blit(msg_surf, (27, SCREEN_SIZE[1]-58))

        # dragging preview
        if dragging_card:
            mx, my = pygame.mouse.get_pos()
            screen.blit(dragging_card["image"], (mx - offset_x, my - offset_y))

        # tooltip
        if hover_idx is not None and slots[hover_idx]["card"]:
            draw_tooltip(slots[hover_idx]["card"]["title"], (mx, my))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
