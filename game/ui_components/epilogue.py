from typing import List

from game.streamlit_compat import st


def get_epilogue_aftermath_lines() -> List[str]:
    """Build ending aftermath details from key flags, events, and trait outcomes."""
    flags = st.session_state.flags
    traits = st.session_state.traits
    lines: List[str] = []

    if flags.get("final_plan_shared"):
        lines.append("Your final pre-assault briefing becomes standard doctrine for Oakrest's defenders.")
    if flags.get("charged_finale"):
        lines.append("Bards celebrate your ferocity, while elders debate the cost of your methods.")
    if flags.get("ember_ridge_vigil_taken"):
        lines.append("The quiet vigil at Ember Ridge becomes a ritual before every future campaign.")

    if flags.get("militia_drilled"):
        lines.append("The militia you drilled forms the core of Oakrest's new shieldwall companies.")
    if flags.get("shadow_routes_marked"):
        lines.append("Your early shadow routes become the town's emergency evacuation grid.")
    if flags.get("archer_watch_established"):
        lines.append("The belltower watch keeps your signal cadence, warning the valley hours in advance.")

    if flags.get("morality") == "merciful" or flags.get("mercy_reputation"):
        lines.append("Families you protected petition Elder Mara to create a standing refuge network.")
    if flags.get("morality") == "ruthless" or flags.get("cruel_reputation"):
        lines.append("Several border hamlets accept your protection, but only behind locked doors and wary silence.")

    if flags.get("opened_cleanly"):
        lines.append("The ruin gate breach leaves fewer graves, and survivors cite your careful approach.")
    if flags.get("tunnel_collapsed"):
        lines.append("Stone crews spend weeks clearing the sealed tunnel, searching for those trapped by your command.")
    if flags.get("rescued_prisoners"):
        lines.append("Former captives rebuild the valley road and openly credit your intervention.")
    if flags.get("rogue_intel_leaked"):
        lines.append("Leaked names from the smuggler ledger keep Oakrest a step ahead of future raids.")
    if flags.get("warrior_line_held"):
        lines.append("Ranger lieutenants teach your barricade stance as the standard for holding lines.")
    if flags.get("archer_routes_marked"):
        lines.append("Ridgewatch signal nests expand along the valley, following your overwatch example.")

    if traits.get("trust", 0) >= 4:
        lines.append("High trust earned you a seat at future war councils, not just a hero's farewell.")
    elif traits.get("trust", 0) <= -2:
        lines.append("Low trust leaves your victories unquestioned, but your motives quietly contested.")

    if traits.get("reputation", 0) >= 5:
        lines.append("Your reputation draws recruits from distant holds, reshaping Oakrest's standing in the region.")

    factions = st.session_state.factions
    if factions.get("dawnwardens", 0) >= 2:
        lines.append("Dawnwarden captains keep a signal fire lit in your honor, promising future mutual defense.")
    if factions.get("ashfang", 0) >= 2:
        lines.append("Ashfang envoys accept a tense truce, naming you as the only outsider they'll parley with.")
    if factions.get("bandits", 0) <= -2:
        lines.append("Bandit crews fracture after your campaign, and river raids drop through the next season.")
    if traits.get("alignment", 0) >= 3:
        lines.append("Your restraint becomes the measure younger scouts are taught to emulate.")
    elif traits.get("alignment", 0) <= -3:
        lines.append("Your brutal efficiency ends the immediate threat, but hardens future conflicts across the frontier.")

    return lines[:7]
