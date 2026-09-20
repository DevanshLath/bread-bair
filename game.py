import random
from dataclasses import dataclass, field


MAX_INVENTORY = 5


@dataclass
class GameState:
    room: str = "crossroads"
    inventory: list[str] = field(default_factory=lambda: ["flour", "iron nail"])
    time_left: int = 24
    mirror_taken: bool = False
    knows_hag_weakness: bool = False
    hag_defeated: bool = False
    lantern_lit: bool = False
    bell_repaired: bool = False
    moonstone_found: bool = False
    score: int = 0
    discoveries: list[str] = field(default_factory=list)
    message: str | None = None
    status: str = "playing"


ROOMS = {
    "crossroads": (
        "The Crossroads",
        "A saint's statue watches over four paths. A cold wind carries the smell "
        "of rain, bread, and something older beneath the earth.",
    ),
    "village": (
        "Morrowfen Village",
        "A handful of cottages crouch behind a crooked palisade. The baker is "
        "still awake, and an unlit lantern hangs beside her door.",
    ),
    "thicket": (
        "The Woven Thicket",
        "Thorns knit themselves across the trail. Something copper-colored glints "
        "inside a nest of black leaves.",
    ),
    "chapel": (
        "The Bell Chapel",
        "The roof has fallen in, but the little bronze bell remains. Its rope is "
        "broken, and a dark stairway descends behind the altar.",
    ),
    "bog": (
        "The Sunken Bog",
        "The River Hag watches from beneath the murky water. Reeds whisper around "
        "her like a crown, and pale lights drift over the mud.",
    ),
    "cave": (
        "The Root-Crypt",
        "Roots twist through a low crypt under the chapel. The darkness feels "
        "thick enough to touch.",
    ),
    "hill": (
        "The Starling Hill",
        "At the top of the hill, the whole forest lies below you. A stone arch "
        "frames the stars, but its empty socket is waiting for something bright.",
    ),
}

STARTING_PATHS = [
    ("Follow the lanterns to Morrowfen Village", "village"),
    ("Push east into the Woven Thicket", "thicket"),
    ("Climb the path to the Bell Chapel", "chapel"),
    ("Follow the muddy track to the Sunken Bog", "bog"),
]


def has(state: GameState, item: str) -> bool:
    return item in state.inventory


def add_item(state: GameState, item: str) -> bool:
    if len(state.inventory) >= MAX_INVENTORY:
        state.message = "Your satchel is full. Find a safe place to leave something."
        return False
    state.inventory.append(item)
    return True


def travel(state: GameState, room: str) -> None:
    state.room = room
    state.time_left -= 1
    state.message = random_travel_event(state)


def random_travel_event(state: GameState) -> str | None:
    if random.random() > 0.35:
        return None

    event, reward = random.choice([
        ("A string of blue fireflies circles you, then points toward the safest path.", 1),
        ("You find a warm blackberry beneath the leaves. The forest is not entirely cruel.", 1),
        ("A branch snaps behind you. You hurry on and lose an hour to the detour.", -1),
        ("A tiny owl watches from a signpost. You feel oddly encouraged.", 2),
    ])
    state.time_left += reward
    if reward > 0:
        state.score += reward
    if reward < 0:
        state.time_left = max(0, state.time_left)
    return event


def room_choices(state: GameState) -> list[tuple[str, str]]:
    if state.room == "crossroads":
        return STARTING_PATHS.copy()
    if state.room == "village":
        choices = []
        if has(state, "flour"):
            choices.append(("Give the baker your flour", "baker"))
        if not state.lantern_lit:
            choices.append(("Take the unlit lantern", "lantern"))
        choices.append(("Return to the Crossroads", "crossroads"))
        return choices
    if state.room == "thicket":
        choices = []
        if not state.mirror_taken:
            choices.append(("Reach into the leaves for the Copper Mirror", "mirror"))
        choices.append(("Return to the Crossroads", "crossroads"))
        return choices
    if state.room == "chapel":
        choices = []
        if has(state, "iron nail") and not state.bell_repaired:
            choices.append(("Repair the chapel bell with the iron nail", "bell"))
        choices.append(("Descend into the Root-Crypt", "cave"))
        choices.append(("Return to the Crossroads", "crossroads"))
        return choices
    if state.room == "cave":
        choices = []
        if state.lantern_lit and not state.moonstone_found:
            choices.append(("Search the crypt by lantern-light", "moonstone"))
        if not state.lantern_lit:
            choices.append(("Feel around in the darkness", "darkness"))
        choices.append(("Climb back to the Bell Chapel", "chapel"))
        return choices
    if state.room == "bog":
        choices = []
        if not state.knows_hag_weakness:
            choices.append(("Listen to the whispering reeds", "reeds"))
        if (
            has(state, "copper mirror")
            and state.knows_hag_weakness
            and not state.hag_defeated
        ):
            choices.append(("Offer the Copper Mirror to the Hag", "hag"))
        if state.hag_defeated:
            choices.append(("Take the Amber Tear", "tear"))
        choices.append(("Return to the Crossroads", "crossroads"))
        return choices
    if state.room == "hill":
        choices = []
        if has(state, "amber tear") and has(state, "moonstone"):
            choices.append(("Place the two treasures in the star arch", "true_end"))
        if has(state, "amber tear"):
            choices.append(("Keep the Amber Tear and leave the forest", "good_end"))
        choices.append(("Return to the Crossroads", "crossroads"))
        return choices
    return []


def take_action(state: GameState, action: str) -> None:
    if action in {"crossroads", "village", "thicket", "chapel", "bog", "cave"}:
        travel(state, action)
    elif action == "baker":
        state.inventory.remove("flour")
        state.lantern_lit = True
        state.score += 2
        state.message = "The baker gives you a brass lantern, already filled with oil."
    elif action == "lantern":
        state.lantern_lit = True
        state.score += 1
        state.message = "You light the lantern. Its small flame makes the forest feel less endless."
    elif action == "mirror":
        if add_item(state, "copper mirror"):
            state.mirror_taken = True
            state.score += 3
            state.discoveries.append("Copper Mirror")
            state.message = "You found a Copper Mirror. Its surface reflects a sky full of stars."
    elif action == "bell":
        state.inventory.remove("iron nail")
        state.bell_repaired = True
        state.score += 3
        state.discoveries.append("Rang the Bell")
        state.message = "The bell rings once. Somewhere far away, a trapped spirit sighs with relief."
    elif action == "darkness":
        state.time_left -= 1
        state.message = "Your hands find old bones. You retreat before the dark finds you."
    elif action == "moonstone":
        if add_item(state, "moonstone"):
            state.moonstone_found = True
            state.time_left -= 1
            state.score += 5
            state.discoveries.append("Moonstone")
            state.message = "The lantern reveals a Moonstone hidden in the roots. It hums in your hand."
    elif action == "reeds":
        state.knows_hag_weakness = True
        state.time_left -= 1
        state.score += 1
        state.message = "The reeds whisper: 'She trades only for copper...'"
    elif action == "hag":
        state.inventory.remove("copper mirror")
        state.hag_defeated = True
        state.score += 5
        if add_item(state, "amber tear"):
            state.discoveries.append("Amber Tear")
            state.message = "The Hag takes the mirror and drops a glowing Amber Tear on the bank."
    elif action == "tear":
        state.room = "hill"
        state.message = "The Tear warms your palm. A hidden trail climbs toward the stars."
    elif action == "good_end":
        state.status = "good_end"
    elif action == "true_end":
        state.status = "true_end"


def show_status(state: GameState) -> None:
    title, text = ROOMS[state.room]
    print("\n" + "=" * 68)
    print(f"{title} | {state.time_left} hours remain")
    print(f"Satchel ({len(state.inventory)}/{MAX_INVENTORY}): {', '.join(state.inventory) or 'empty'}")
    print(f"Score: {state.score}")
    print("=" * 68)
    print(text)
    if state.message:
        print(f"\n{state.message}")


def print_help() -> None:
    print("\nEnter a number to choose an action.")
    print("i = inspect your satchel, h = help, q = leave the forest")
    print("Explore carefully: some discoveries unlock a better ending.")
    print("Random forest events can help or hinder you, so every journey is different.")


def play() -> None:
    state = GameState()
    random.shuffle(STARTING_PATHS)
    print("The Last Lantern: A Text Adventure")
    print("Find the Amber Tear before the third sunrise. The forest remembers what you do.")

    while state.status == "playing":
        if state.time_left <= 0:
            state.status = "lost"
            break

        show_status(state)
        choices = room_choices(state)
        print()
        for number, (label, _) in enumerate(choices, start=1):
            print(f"{number}. {label}")

        answer = input("\nAction (h for help): ").strip().lower()
        if answer == "q":
            print("You leave the forest while the path is still visible.")
            return
        if answer == "h":
            print_help()
            continue
        if answer == "i":
            print(f"\nYou carry: {', '.join(state.inventory) or 'nothing'}")
            continue
        if not answer.isdigit() or not 1 <= int(answer) <= len(choices):
            state.message = "That is not an available action. Type h for help."
            continue
        take_action(state, choices[int(answer) - 1][1])

    if state.status == "true_end":
        print("\nThe Amber Tear and Moonstone awaken the star arch.")
        print("Dawn breaks across Morrowfen. You saved the forest and became its new guardian.")
    elif state.status == "good_end":
        print("\nYou acquired the Amber Tear and survived the trial of the woods.")
        print("The forest shall remember your name.")
    else:
        print("\nThe third sun rises. The woods have claimed you.")
    print(f"Final score: {state.score}")
    if state.discoveries:
        print("Discoveries: " + ", ".join(state.discoveries))


if __name__ == "__main__":
    play()
