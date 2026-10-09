# D-0016: Roads vs. walkways, and arriving by train

| | |
|---|---|
| **Status** | Awaiting review (two parts, each with its own decision box) |
| **Raised** | 2026-10-09. Part 2 added the same day at your request |
| **Affects** | Part 1: the map, tiles, Orientation Leader dialogue, a possible moving Ram Van later. Part 2: the opening of the game, the start point (**would replace D-0015**), Orientation Leader placement |
| **Built provisionally?** | Part 1: yes, Option A. Part 2: no, waiting for your decision |

Both parts are about **how students get around and arrive on campus**, so they share this file.

---

# Part 1: Roads vs. walkways

## What's being decided

On the real campus, students need to tell **roads** (Ram Van shuttle, service and visitor vehicles) apart from **walkways**. That raises three questions:
1. How does the game show the difference?
2. Can the player walk on roads?
3. Which roads count as roads?

### What I built from the official map and photos

- **Roads:** gray asphalt with **sidewalks along both sides**, wherever there's room. You assumed sidewalks along the main roads, and the map draws the roads as wide bands.
- **Walkways:** warm brick pavers, like the walkway in front of Walsh Library in your photo.
- **Crosswalks:** white stripes wherever a walkway crosses a road. They're placed automatically, and the stripes always run across the road.
- **Guard booths:** at Matteo Ricci Circle and the Webster Avenue gate (from the gate photo and the map legend).
- **Gate entrances:**
  - The **Main Entrance** and the **Webster Avenue gate** have road entrances. The Webster gate also has a pedestrian gate beside it, as in the photo.
  - The **Bathgate** and **Clavius Way** gates are walkway-only, since the map labels them "Pedestrian Entrance."
- **The Orientation Leader** now says: *"The gray roads are for the Ram Van shuttle and service vehicles, so stick to the sidewalks and cross at the striped crosswalks."*

### Which roads I treated as roads (please check with Fordham)

| Road | Why I think it's a road |
|---|---|
| Xavier Way | Runs from the Main Entrance, which the map labels "Vehicular Entrance" |
| Matteo Ricci Circle | Roundabout with a guard booth |
| Constitution Row | Wide band from the circle past the Victory Bell |
| Bellarmine Road | Wide band, named "Road" |
| Rose Hill Manor Drive | Wide band, with a Ram Van stop by Dealy Hall |
| Edgar Allan Poeway | Wide band, with Ram Van stops by Cunniffe House and the Alumni Court circle |
| Mill River Road | Wide band leading to the Webster Ave gate, which has a vehicle gate in your photo |
| Old Elm Road | Named "Road" on the official map |
| Clavius Way | Wide band along the south side |

**Open questions:**
- Which of these are open to everyday traffic, and which are shuttle and service vehicles only?
- **Old Elm Road** appears in different places: the official map puts it in the southwest by Walsh Lawn, while Google Maps labels "Old Elm Rd" near Martyrs' Court and Collins Hall. I followed the official map.
- I left out smaller service roads (behind McShane and Lombardi, the parking garage access road, and Archer Drive along the railway). They can be added if they matter to students.

## Options

### A. Show roads clearly, but let the player walk on them (recommended, already built)
- **Pros:**
  - Students learn to *recognize* roads, sidewalks and crosswalks.
  - No frustration from invisible walls.
  - Matches reality: you *can* cross a campus road, you should just do it carefully.
- **Cons:** The game doesn't enforce using crosswalks.

### B. Roads are blocked except at crosswalks
- **Pros:** Forces the crosswalk habit.
- **Cons:**
  - Roads become walls, so getting around becomes a maze.
  - We'd need many more crosswalks than really exist.
  - Feels unrealistic and annoying.

### C. Option A plus a moving Ram Van shuttle on its real route (a later feature)
- **Pros:**
  - Makes the campus feel alive.
  - Teaches where the shuttle actually goes, which is useful for checklist step 6 (D-0014).
- **Cons:**
  - Needs the real route and schedule from Fordham.
  - Needs vehicle movement code and rules for when the van and the player meet.
  - Adds scope. Best after M4.

## My recommendation

**Option A now. Consider C after M4** if Fordham can share the Ram Van route. A teaches what students most need to recognize, without turning the map into a maze. Either way, someone at Fordham should confirm the road list above. Changing a road into a walkway, or the reverse, is a quick map edit.

## Your decision (Part 1)

- [ ] **Approve**: go with Option A (C revisited after M4)
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 2: Opening sequence, arriving by train

## What's being decided

You asked for the game to open with a short animated arrival:
1. The player character is **sitting on a Metro-North train**.
2. They **get off at Fordham station** and walk out of the station.
3. They walk to the **Third / Webster Avenue Gate**, the southwest gate right by the station.
4. Along the way, short captions share **information about Fordham**.
5. A screen shows the **main controls**.
6. The player then **walks through the gate themselves** to start the game.

This would change **where the game starts**. D-0015 (approved) put the start at the Main Entrance on Southern Boulevard. This puts it at the Webster Avenue gate in the southwest corner, so approving Part 2 **replaces D-0015**.

### Proposed storyboard (about 30–40 seconds, skippable)

| # | Scene | What happens | Caption (draft, to be checked by Fordham) |
|---|---|---|---|
| 1 | **On the train** (side view inside a train car) | The character sits by the window. City buildings scroll past outside | *"Metro-North. Next stop: Fordham."* then *"Your first week at Fordham University starts today."* |
| 2 | **Fordham station** | The train slows and the doors open. The character steps onto the platform and walks out of the station | *"Fordham is a Jesuit university, founded in 1841."* |
| 3 | **Webster Avenue** (side view of the street) | The character walks along the sidewalk to the gate: stone pillars, black iron gates, guard booth and the maroon Fordham sign, as in `research/images/entrance_by_train.png` | *"Rose Hill, here in the Bronx, is Fordham's original campus."*, *"Fordham also has campuses at Lincoln Center in Manhattan and in Westchester."*, *"Fordham's teams are the Rams. You'll see the Ram all over campus."* |
| 4 | **Controls card** (waits for the player) | A simple panel with the controls | **Move:** arrow keys / WASD. **Talk, read, open a card:** Z / Space / Enter. **Back, skip text:** X. **Campus Guide:** Tab (arrives in M3). **Tip:** "Gray = road, tan = walkway. Cross at the crosswalks." |
| 5 | **Gameplay starts** (top-down, the normal view) | The player stands on the Webster Avenue sidewalk just outside the gate. Walking through it shows a "Welcome to Rose Hill" banner, and an Orientation Leader waits just inside | The Orientation Leader's welcome (moved here from the Main Entrance) |

**Details either way:**
- **Skippable:** pressing X at any time jumps straight to the controls card. Once saving exists (M3), returning players can skip the whole intro.
- **Captions advance on their own**, or sooner if you press Z, so slow and fast readers are both fine.
- **Captions live in a data file** (`content/intro.json`), like the rest of the text (D-0006), so staff can edit the facts without touching code.
- **No transit logos:** the train is drawn generically, and "Metro-North" appears only as text (same rule as D-0009).
- **Map change:** a short strip of the Webster Avenue sidewalk is added below the gate, so the player can step *through* the gate rather than appear inside it.

## Options

### A. Animated arrival by train, ending at the Webster Avenue gate (recommended)
- **Pros:**
  - Strong, memorable opening that tells a story.
  - Teaches the **real commuter route** (Metro-North → Fordham station → Webster Ave gate), which many students and families will actually use. It sets up checklist step 6 ("learn how to get off campus") from minute one.
  - School facts land naturally while something is happening on screen.
  - Walking through the gate yourself is a satisfying "the game begins" moment.
- **Cons:**
  - New art: a train interior, a platform and a street scene (placeholder quality first, like everything else, D-0008).
  - The start is in the southwest corner, about 10–15 seconds' walk from Edwards Parade. The Orientation Leader at the gate points the way (Mill River Road → Old Elm Road → past Dealy Hall).
  - About 1–2 days of work at placeholder quality.

### B. Illustrated slides instead of animation
- The same story and captions as still pictures (train, station, gate), then the controls card.
- **Pros:** About half the work, and easier to replace with real photos or artwork later.
- **Cons:** Less charming. It feels like a slideshow before the game, not part of it.

### C. Let the player choose how they arrive: by train (Webster Ave gate) or by car or Ram Van (Main Entrance)
- **Pros:** Covers commuters and drivers. Both gates get taught.
- **Cons:** Two openings to build and maintain, and a choice before the player even knows the campus. Better as a later addition to A.

### D. No intro: keep the current start at the Main Entrance (D-0015) and put the controls on the title screen
- **Pros:** No extra work.
- **Cons:** Misses the storytelling and the transit lesson you're after.

## My recommendation

**Option A.** It does exactly what you described, and it earns its place as an onboarding tool: the first thing a new student learns is a route they will really use. The cons are manageable. Placeholder art keeps it cheap, it can be skipped, and the Orientation Leader at the gate fixes the "start in a corner" problem. **Option C** is a nice follow-up once A exists.

**If approved, I will:**
1. Mark **D-0015 as superseded** by this part.
2. Add `content/intro.json` and an intro scene with the five beats above.
3. Add the Webster Avenue sidewalk strip and move the start and the Orientation Leader to the gate.
4. Update the screenshot tool and the tests.

**Facts to confirm with Fordham:**
- The captions above.
- The train details. I believe Fordham station is served by Metro-North trains from Grand Central, but to be safe the caption only says "Metro-North."

## Your decision (Part 2)

- [ ] **Approve**: go with Option A (and D-0015 is superseded)
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below (for example, changes to the storyboard or captions)

**Your notes:**

>

