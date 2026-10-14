# D-0042: Public Safety officers and card readers at every gate

| | |
|---|---|
| **Status** | Decided 2026-10-14: Parts 1 to 4 approved (A, A). Built on branch `gate-guards` |
| **Raised** | 2026-10-14. Only the Webster Avenue gate has a guard. Every gate should have a Public Safety officer and a card reader, like the real campus. The other gates can stay open |
| **Affects** | The three entrances other than Webster Avenue, the gate booth in Matteo Ricci Circle, and the gates' cards in the game and the Campus Guide |
| **Built?** | Yes, on branch `gate-guards` |

## What's there today

| Entrance | Officer | Card reader | Can you walk through? |
|---|---|---|---|
| Third / Webster Avenue gate (southwest) | Bert | Yes, the gate opens when you tap in | After the ID check, which is the tutorial at the start |
| Main Entrance, Southern Boulevard (northeast, where Xavier Way leaves campus) | No | No | Yes |
| Pedestrian Entrance, Bathgate Avenue (south end of Rose Hill Manor Drive) | No | No | Yes |
| Pedestrian Entrance, Clavius Way (east, by Tierney Hall) | No | No | Yes |

There's also an empty guard booth in Matteo Ricci Circle, inside the Main Entrance. The Orientation Leader there mentions it.

**What we know about the real campus:**
- Fordham's gates are staffed by Public Safety, and students tap their Fordham ID to get in.
- A 2014 article in The Fordham Ram mentions a round-the-clock guard at the Bathgate entrance, and a guard plus an ID turnstile at the gate by Walsh Hall.
- That's old, so current staffing and hours should be confirmed with Public Safety.

---

# Part 1: A Public Safety officer at each gate

A **Public Safety Officer** stands just inside each of the three gates, beside the gateposts. They:
- look like Bert, in the same guard uniform, so players learn the look
- stand still and never wander (decision 0040), so you always find them at their gate
- turn to face you when you talk to them

**What they say** (first drafts; edit freely):

**Main Entrance:**
- "This is the Main Entrance on Southern Boulevard. Cars, the Ram Van and visitors come in here."
- "Walking in? Tap your Fordham ID at the reader. Visitors check in with us."
- "Public Safety is here around the clock. Our office is in Thebaud Hall if you ever need us."

**Bathgate Avenue:**
- "This is the Bathgate Avenue gate, at the south end of campus by Thebaud and Finlay Halls."
- "Tap your Fordham ID at the reader whenever you come in."
- "Lost something, or need help? Public Safety is in Thebaud Hall, right up the road."

**Clavius Way:**
- "This is the Clavius Way gate, on the east side by Tierney Hall."
- "Tap your Fordham ID at the reader on your way in."
- "Save Public Safety's number in your phone today. You'll be glad you have it."

The last lines point to Public Safety in Thebaud Hall, which ties in with the Lost and Found mission.

## Your decision (Part 1)

- [x] **Approve**
- [ ] **Not approve**: say why
- [ ] **Other**: changes to the lines, or where they stand

**Your notes:**

>

---

# Part 2: A card reader at each gate

Each of the three gates gets a **card reader**: a short dark post with a reader panel and a small green light. It stands beside the opening, on the side people walk in on.

**The gates stay open, as you said.**
- You can walk straight through.
- Face the reader and press Z to tap your ID: "You tap your Fordham ID. *Beep!* The light turns green." That's the same tap you learned at the Webster Avenue gate, and it mimics what you do in real life.
- The card for each gate (Z on its sign) says that you tap your ID here and a Public Safety officer is on duty.

**Webster Avenue doesn't change.** Its gate stays closed until you tap in. That's the game's tutorial, and Bert stays.

### A. Open gates, with a reader you can tap (recommended, as you asked)

- **Pros:**
  - Looks and feels like the real campus.
  - Nothing ever blocks you.
  - It repeats the tap-your-ID habit.
- **Cons:** tapping at these gates is optional, so some players won't bother.

### B. Every gate closed until you tap, like Webster Avenue

- **Pros:** the most like real life.
- **Cons:** players start inside campus and can't go outside, so these checks would only ever happen in reverse. They'd mostly get in the way.

## Your decision (Part 2)

- [x] **Approve**: A
- [ ] **Not approve**: say which option you'd prefer
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 3: The empty booth in Matteo Ricci Circle

### A. Put an officer in the booth too (recommended)

The Orientation Leader at the Main Entrance already says you drive in "past the guard booth in Matteo Ricci Circle", and an empty booth looks like a mistake. A second officer would stand at the booth window, saying something like: "Driving in? Show your parking permit or check in here. Parking is in the lot by Southern Boulevard."

Whether the real booth is staffed should be confirmed with Fordham.

### B. Leave the booth empty

The officer at the gate is enough.

## Your decision (Part 3)

- [x] **Approve**: A
- [ ] **Not approve**: B, leave it empty
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 4: Updating the gates' descriptions (and the Campus Guide)

The three gates' descriptions in `content/locations.json` will say that a Public Safety officer is on duty and that you tap your Fordham ID at the reader. The accessible Campus Guide is built from the same descriptions (decision 0037), so it updates automatically.

## Your decision (Part 4)

- [x] **Approve**
- [ ] **Other**: describe below

**Your notes:**

>

---

## Later: gates the game doesn't have yet

The same 2014 article names other gates the map doesn't show:
- the **Walsh Hall gate**, with an ID turnstile
- the **FMH gate**, by Faculty Memorial Hall
- the **Finlay gate**, which may be the Bathgate entrance under another name

Adding them means changing the fence, and placing them right needs someone who knows the campus. I'd put them on the list of facts to check with Fordham (Public Safety or Facilities) rather than guess. Once we know where they are and whether they're staffed, each one gets the same officer and reader.

## To confirm with Fordham

- Which gates are staffed, and when (24 hours, or set hours)?
- Do the pedestrian gates have card readers or turnstiles?
- Is the Matteo Ricci Circle booth staffed?
- Where exactly are the Walsh, FMH and Finlay gates?
- Public Safety's phone number, if you'd like an officer to give it.

## What I'll build after your decisions

- **Three officers in `content/maps/rose_hill.json`:** "Public Safety Officer", Bert's sprite, no wandering. Plus the booth officer if you approve Part 3.
- **A new `card_reader` tile and a reader object at each gate.** Facing it and pressing Z shows the tap lines. It's drawn as a post with a reader and a green light.
- **New wording for the three gates in `content/locations.json`.**
- **Tests:**
  - every entrance has an officer and a reader within a couple of tiles of its opening
  - every gate other than Webster can still be walked through
  - the Campus Guide mentions the reader at each gate
- **Before-and-after screenshots** of each gate, added here.

## Sources
- [Walsh gate to remain open 24/7 (The Fordham Ram, 2014)](https://thefordhamram.com/news/walsh-gate-to-remain-open-247)
- [Walsh gate is now open 24 hours (The Fordham Ram)](https://thefordhamram.com/news/walsh-gate-is-now-open-24-hours)

## What was built (2026-10-14)

**Pictures** (in `decisions/images/0042/`):
- `gates.png`: each gate and the booth, today and now
- `bathgate_closeup.png`: the Bathgate gate up close, with the officer beside the gatepost and the card reader beside the sign

**Officers.** A "Public Safety Officer" in Bert's uniform at each place, with the lines above. None of them wander.

| Where | Officer stands | Card reader |
|---|---|---|
| Main Entrance | (79, 23), on the walkway beside the gatepost | (79, 21), on the lawn beside the gatepost |
| Bathgate Avenue | (42, 65), beside the east gatepost, facing the opening | (39, 65), beside the west gatepost, under the gate's sign |
| Clavius Way | (81, 59), beside the east gatepost | (78, 59), beside the west gatepost |
| Matteo Ricci Circle booth | (76, 42), next to the booth | none |

**Card readers.** A new `card_reader` tile: a dark post on a small paved square, with a reader that has a maroon Fordham band, a card slot and a green light. Face it and press Z: "You tap your Fordham ID on the card reader." / "Beep! The light turns green." The gates stay open, and Webster Avenue is unchanged.

**Gate descriptions** (`content/locations.json`):
- Each open gate's card now says a Public Safety officer is on duty and you tap your Fordham ID at the card reader.
- The Main Entrance card also mentions the booth in Matteo Ricci Circle.
- The Campus Guide pages for the three gates picked this up automatically.

**Tests:** 278 pass. The new `tests/test_gates.py` checks that:
- every open gate has an officer (who doesn't wander) and a card reader within 3 tiles of its opening
- Webster keeps Bert and its ID check
- the booth has an officer
- you can still walk to every open gate's opening
- each gate's card mentions the officer and the reader

The accessibility check passes: 60 pages, 0 problems.

**Still to confirm with Fordham:** the questions above, especially the booth's parking-permit line and the gates' hours.

