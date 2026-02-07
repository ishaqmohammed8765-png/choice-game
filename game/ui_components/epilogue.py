from typing import List

from game.streamlit_compat import st


def get_epilogue_aftermath_lines(*, max_lines: int | None = 9) -> List[str]:
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
    if flags.get("ember_ridge_vigil_spoken"):
        lines.append("Your pre-assault words at Ember Ridge are repeated as a vow among new recruits.")
    if flags.get("ember_ridge_vigil_walked"):
        lines.append("Scouts chart your ridge walk as the template for pre-battle recon patrols.")
    if flags.get("causeway_quiet_marked"):
        lines.append("The causeway footing you marked is now carved into the ranger manuals.")
    if flags.get("causeway_quiet_steadied"):
        lines.append("The causeway's hush becomes part of the tale told to test courage in silence.")

    if flags.get("militia_drilled"):
        lines.append("The militia you drilled forms the core of Oakrest's new shieldwall companies.")
    if flags.get("shadow_routes_marked"):
        lines.append("Your early shadow routes become the town's emergency evacuation grid.")
    if flags.get("archer_watch_established"):
        lines.append("The belltower watch keeps your signal cadence, warning the valley hours in advance.")
    if flags.get("warrior_oath_taken"):
        lines.append("Your warrior's oath is etched into the palisade as a reminder of steadfast resolve.")
    if flags.get("rogue_oath_taken"):
        lines.append("Rogues in Oakrest swear by your alleyway vow when they take their first contracts.")
    if flags.get("archer_oath_taken"):
        lines.append("Archers carve your opening signal into their bow grips as a charm against surprise.")

    if flags.get("echo_locket_claimed"):
        lines.append("The Echo Locket hums in your pack, a thread connecting this journey to every one that follows.")
    if flags.get("ember_sigil_claimed"):
        lines.append("The Ember Sigil's warmth lingers on your skin, a brand that marks you across lifetimes.")
    if flags.get("dawn_relic_claimed"):
        lines.append("The Dawn Relic's light steadies in your hands — the uncorrupted heart of the old kingdom now travels with you.")
    if flags.get("legacy_ending"):
        lines.append("You carried relics across lifetimes to undo Caldus's corruption from within. The valley will not forget the weight of that persistence.")

    if flags.get("morality") == "merciful" or flags.get("mercy_reputation"):
        lines.append("Families you protected petition Elder Mara to create a standing refuge network.")
    if flags.get("morality") == "ruthless" or flags.get("cruel_reputation"):
        lines.append("Several border hamlets accept your protection, but only behind locked doors and wary silence.")

    if flags.get("kest_informant"):
        lines.append("Kest's intelligence on Caldus's network helps dismantle sleeper cells throughout the valley.")
    if flags.get("kest_intel_available") and flags.get("spared_bandit"):
        lines.append("Kest settles quietly in Oakrest, offering counsel on old kingdom ruins to any who ask.")
    if flags.get("council_cowed"):
        lines.append("The war council never fully recovers from being forced into a reckless push under your command.")

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
    if flags.get("dawnwarden_allied"):
        lines.append("Dawnwarden banners fly beside Oakrest colors, a reminder of the alliance you forged.")
    if flags.get("ashfang_allied"):
        lines.append("Ashfang drums echo at winter markets, a tense but lasting symbol of your pact.")
    if flags.get("serin_endorsement"):
        lines.append("Serin's endorsement keeps rival captains from contesting your battlefield authority.")
    if flags.get("drogath_endorsement"):
        lines.append("Drogath's backing keeps the most ruthless fighters in line, if only barely.")
    if flags.get("tidebound_knight_defeated"):
        lines.append("With Sir Edrin freed from Caldus's warding, the causeway becomes a safer trade lane.")
    if flags.get("pyre_alchemist_defeated"):
        lines.append("Without Vorga's forge, Caldus's firebomb stockpile vanishes from battle reports.")
    if flags.get("skipped_causeway_boss_returned"):
        lines.append("Sir Edrin's unresolved corruption haunts the valley — sightings near the causeway persist for months.")
    if flags.get("skipped_mill_boss_returned"):
        lines.append("Vorga's survival means Caldus's bomb recipes persist. Border villages invest in firebreaks.")

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

    ember_tide = traits.get("ember_tide", 0)
    if ember_tide >= 7:
        lines.append("The Ember Tide rose unchecked for too long. Outer farms remain scarred for years, and refugees settle uneasily in Oakrest proper.")
    elif ember_tide >= 5:
        lines.append("The Ember Tide burned hot before you stopped it. Several farmsteads must be rebuilt from ash.")
    elif ember_tide >= 3:
        lines.append("The Ember Tide left its mark, but early action spared Oakrest's outer settlements the worst.")
    elif ember_tide <= 1:
        lines.append("Your swift action kept the Ember Tide from ever truly threatening the valley.")

    if max_lines is None:
        return lines
    return lines[:max_lines]
