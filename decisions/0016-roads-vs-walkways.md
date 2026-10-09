# D-0016: Roads vs. walkways

| | |
|---|---|
| **Status** | Awaiting review |
| **Raised** | 2026-10-09 |
| **Affects** | The map, tiles, Orientation Leader dialogue, and a possible moving Ram Van later |
| **Built provisionally?** | Yes, Option A. Changing to B is a small code change. C is a new feature. |

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

## Your decision

- [ ] **Approve**: go with Option A (C revisited after M4)
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>
