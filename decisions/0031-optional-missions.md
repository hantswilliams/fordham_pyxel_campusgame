# D-0031: Optional missions (side quests), written as data files

| | |
|---|---|
| **Status** | Awaiting review |
| **Raised** | 2026-10-11. You asked for something like Pokémon's missions, with no fights: optional, and written in a format we can reuse |
| **Affects** | New `content/missions/` folder, a small mission engine, NPC dialogue, the TAB menu (Campus Guide, M3), save data, the First Week Checklist (D-0014) |
| **Built provisionally?** | No. Nothing is built until you've ticked the boxes below |

## What's being decided

Students already walk, ride, read cards and talk to people. Missions would give them small, optional reasons to go to places they'll need in their first week. Pokémon has battles. Ours would be errands, scavenger hunts, timed bike runs and quick questions.

There are five things to decide:

1. **The format.** How a mission is written down so anyone can add one by copying a file.
2. **The building blocks.** What a mission step can be.
3. **How players find and track missions.**
4. **Rewards.**
5. **Which missions to make first.** There's a list of ideas to pick from.

---

# Part 1: The format

### A. One JSON file per mission in `content/missions/`, from a template (recommended)

Each mission is one file, like the building folders. To add a mission, you copy `_TEMPLATE.json`, fill it in and run the tests. The tests catch mistakes, for example:
- a step that points at a place, a person or an object that doesn't exist on the map;
- a question with no correct answer.

An example, the "Lost ID" mission from Part 5:

```json
{
  "id": "lost_id",
  "title": "Lost and Found",
  "summary": "A student dropped their Fordham ID near McShane. Find it and take it to Public Safety.",
  "optional": true,
  "giver": {"npc": "Worried Student", "at": [46, 30]},
  "teaches": ["Public Safety is in Thebaud Hall", "Lost IDs go to Public Safety"],
  "requires": [],
  "steps": [
    {"do": "talk",  "npc": "Worried Student",
     "say": ["I dropped my ID somewhere between McShane and Edwards Parade!"]},
    {"do": "find",  "item": "fordham_id", "at": [49, 33], "tile": "item_card",
     "say": ["You found a Fordham ID card on the path."]},
    {"do": "go_to", "location": "thebaud_hall",
     "say": ["Public Safety logs the ID and contacts the owner."]}
  ],
  "reward": {"stamp": "lost_and_found", "badge": "wellness"},
  "done_say": ["Thanks! Now you know where Public Safety is if you ever need it."]
}
```

- **Pros:**
  - Staff can write missions without touching code (D-0006, content as data).
  - Each mission is self-contained, so they're easy to review, reorder or switch off.
  - The tests keep every mission working when the map changes.
- **Cons:** We need a small engine to read the files. That's a one-time cost, sized in Part 2.

### B. All missions in one `content/missions.json`

- **Pros:** Everything is in one place.
- **Cons:** The file gets long, edits clash, and it's harder to switch one mission off.

### C. Missions written in Python

- **Pros:** Anything is possible.
- **Cons:** Only a programmer can write or fix one, which goes against D-0006.

## Your decision (Part 1)

- [ ] **Approve**: go with Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 2: The building blocks (step types)

Every mission is a list of steps, and each step is one of a few kinds. New missions mix the kinds; they don't need new code.

| Step | What the player does | Already in the game? |
|---|---|---|
| `talk` | Talk to a named person | Yes: NPCs |
| `go_to` | Walk up to a building's door or a landmark's sign | Yes: doors and signs |
| `read` | Open a place's card (Z on its door or sign) | Yes: cards |
| `find` | Pick up an item placed on the map (it shows as a small sparkle tile) | New: one object type plus the sparkle art |
| `answer` | Answer a multiple-choice question about something nearby | New: a choice box, like Bert's ID check |
| `ride` | Get somewhere on the bike, optionally before a timer runs out | New: a timer, reusing the bike (D-0030) |
| `collect` | Do *n* of a set, in any order (for example, visit 3 of 5 landmarks) | New: a counter |

- Each step can show lines (`say`) when it's done, and a hint (`hint`) the player can see in the mission log.
- **Optional by design:**
  - Missions never block the gate, the map or the First Week Checklist.
  - A player can drop a mission and start it again.
- **Cost:** about the size of the ID check and the bike put together. The engine is pure logic, like `bike.py`, so it can be fully tested.

### A. These seven step types (recommended)

### B. Start with only `talk`, `go_to` and `read`

- **Pros:** Smallest build.
- **Cons:** Missions are just "walk here, read this", which is less fun.

## Your decision (Part 2)

- [ ] **Approve**: go with Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 3: How players find and track missions

### A. Pokémon-style: an NPC with a "!" offers it, a log tracks it (recommended)

- **Starting a mission:** a person with a mission shows a small maroon **"!"** above their head. Talking to them offers the mission: "Can you help? YES / NOT NOW".
- **Mission Log:** the **TAB** menu gets a *Missions* tab next to the Campus Guide (M3). It lists active, available and finished missions, with each mission's current step and hint.
- **Tracker:** a one-line tracker at the top-left shows the current step, for example "Find the lost ID (near McShane)". You can turn it off.
- **Map pins:** the campus map (M) puts a small "!" pin on the current target.
- **Finishing:** a short jingle and a "MISSION COMPLETE" banner, once there's audio.

### B. A notice board at McShane lists every mission

- **Pros:** One place to find them all.
- **Cons:** Less Pokémon. Players who never go to McShane never see the missions.

### C. Both A and B

- **Pros:** NPCs offer missions as you explore, and the board catches anything you missed.
- **Cons:** A bit more to build.

## Your decision (Part 3)

- [ ] **Approve**: go with Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below (for example, C)

**Your notes:**

>

---

# Part 4: Rewards

### A. Stamps in a "Ram Passport", plus the badges from D-0003 (recommended)

- **Stamps:** each finished mission adds a stamp to a passport page in the TAB menu. Fill it to unlock an end card that links to the real orientation page.
- **Badges:** missions can also count towards the five badges from D-0003 (Academics, Wellness, Community, Career, Dining). That's one reward system, not two.
- **Fun extras:** a few unlocks, all original art, nothing branded. For example, a maroon bike after the bike mission, or a hat for your character.
- **Pros:** Collecting is the pull Pokémon has (D-0003), and every stamp ties to a real place.

### B. Badges only

- **Pros:** Simplest.
- **Cons:** Only five slots, so most missions wouldn't feel rewarded.

### C. Points and a leaderboard

- **Cons:** It needs a server and accounts, and turns orientation into a competition.

## Your decision (Part 4)

- [ ] **Approve**: go with Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 5: Mission ideas. Tick the ones to make

Each idea teaches something real. Time is for a first-time player. "Needs Fordham" means a fact we should check before shipping.

| ✓ | Mission | The story | What it teaches | Steps used | Time | Needs Fordham? |
|---|---|---|---|---|---|---|
| [ ] | **1. Lost and Found** | A student dropped their ID near McShane. Find it and take it to Public Safety | Where Public Safety is; what to do with a lost ID | talk, find, go_to | 3 min | That lost IDs go to Public Safety in Thebaud |
| [ ] | **2. Ram Van Run** | Make it to the shuttle stop by Dealy before the Ram Van leaves, on the bike | Shuttle stops; the bike | ride (timer), read | 2 min | Shuttle stop locations (already on the cards) |
| [ ] | **3. Study Spot Scout** | Your roommate wants a quiet place to study. Check out three spots and report back | Walsh Library, McShane, a lawn | collect (3 of 4), talk | 4 min | Which spaces are open for studying |
| [ ] | **4. Landmark Photo Hunt** | The campus paper wants photos of five landmarks | Ram Statue, Victory Bell, Archbishop Hughes Statue, Cunniffe Fountain, Seismic Observatory | collect (5), answer | 6 min | No: the facts are already on the cards |
| [ ] | **5. Bike Courier** | Deliver a package from the McShane mail room to O'Hare before time runs out | McShane, O'Hare, the bike | find, ride (timer) | 2 min | Where the mail room is |
| [ ] | **6. Game Day** | Help the Athletics staffer get ready: ring the Victory Bell, find Moglia Stadium, check the gym's court | Athletics venues, traditions | collect (3), answer | 4 min | The Victory Bell tradition |
| [ ] | **7. Wellness Walk** | A friend is feeling overwhelmed. Find where they can get help | Health Center and Counseling (O'Hare); a calm walk round Edwards Parade | go_to, read, talk | 3 min | **Yes**: office locations and hours. The wording would be reviewed by Counseling |
| [ ] | **8. Dining Passport** | Try three places to eat on campus | McShane Marketplace, Campbell, Queen's Court and O'Hare dining | collect (3 of 4) | 5 min | Which dining spots are open to first-years |
| [ ] | **9. History Detective** | A professor leaves questions on three plaques | Cunniffe House (the old manor), Rose Hill Gym (1925), University Church (1845) | go_to, answer ×3 | 5 min | The facts are on the cards; a quick check |
| [ ] | **10. Campus Tour Guide** | A visiting family is lost. Walk them to Admission in Duane Library, and they follow you | Admission, and giving directions | talk, go_to (with someone following) | 3 min | No. Needs a "someone following you" feature (a bit more build) |
| [ ] | **11. Commuter's Day** | Come in by Metro-North, find the Ram Van, find the parking garage | The Webster gate, shuttle stops, Regional Parking | collect, read | 4 min | A commuter lounge, if there is one |
| [ ] | **12. Copper Beech Count** | Count the purple-leaved trees round Walsh Lawn for the biology club | A light nature mission in the southwest | collect (count) | 3 min | No. Just for fun |

**My recommendation for the first batch:**
- **1 Lost and Found:** errands.
- **2 Ram Van Run:** the bike and a timer.
- **4 Landmark Photo Hunt:** collecting.
- **9 History Detective:** questions.

Together they use every step type except "someone following you", and none needs much from Fordham. **7 Wellness Walk** is valuable, but should wait until Counseling has reviewed the wording.

**Your notes (more ideas welcome):**

>

---

# Part 6: The First Week Checklist as the main mission

### A. Write the checklist (D-0014) in the same format, as the one required mission (recommended)

- It becomes `content/missions/first_week.json`, with `"optional": false`.
- It always shows first in the Mission Log.
- **Pros:** One engine, one format and one log for everything. Changing the checklist becomes a content edit.
- **Cons:** None I can see. The checklist isn't built yet (it's M4).

### B. Keep the checklist separate from missions

- **Cons:** Two systems doing the same job.

## Your decision (Part 6)

- [ ] **Approve**: go with Option A
- [ ] **Not approve**
- [ ] **Other**

**Your notes:**

>

---

## What needs to come first

**Saving progress.** Missions need the game to remember things between sessions (M3's Progress and Save, in ARCHITECTURE.md §3). I'd build saving first, then the mission engine, then the first batch of missions.

**After you've reviewed this, I would build:**
1. Saving and loading progress, which also remembers the bike and the places you've visited.
2. The mission engine and its tests.
3. `content/missions/_TEMPLATE.json`, plus a short how-to in `content/missions/README.md`.
4. The missions you ticked in Part 5.
5. The "!" markers, the Missions tab, the tracker and the map pins.
