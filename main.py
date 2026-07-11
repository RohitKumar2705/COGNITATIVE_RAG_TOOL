"""
Grid07 AI Assignment — Full Runner
Runs all three phases in sequence and logs output.
"""

import json
import sys
import os
import importlib.util

# Add current directory to path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Dynamic import to handle uppercase filenames on case-sensitive systems
def load_module_from_file(module_name, filepath):
    """Load a module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load modules
phase1_module = load_module_from_file("phase1_router", os.path.join(os.path.dirname(__file__), "PHASE1_ROUTER.PY"))
phase2_module = load_module_from_file("phase2_content_engine", os.path.join(os.path.dirname(__file__), "phase2_content_engine.py"))
phase3_module = load_module_from_file("phase3_combat_engine", os.path.join(os.path.dirname(__file__), "phase3_combat_engine.py"))

# Get functions from loaded modules
build_persona_index = phase1_module.build_persona_index
route_post_to_bots = phase1_module.route_post_to_bots
run_content_engine = phase2_module.run_content_engine
generate_defense_reply = phase3_module.generate_defense_reply
PARENT_POST = phase3_module.PARENT_POST
COMMENT_HISTORY = phase3_module.COMMENT_HISTORY
NORMAL_HUMAN_REPLY = phase3_module.NORMAL_HUMAN_REPLY
INJECTED_HUMAN_REPLY = phase3_module.INJECTED_HUMAN_REPLY

BOT_A_PERSONA = (
    "You are Bot A — a Tech Maximalist. You fervently believe AI and technology "
    "are solving humanity's problems. You are data-driven, dismissive of technophobes, "
    "and aggressively optimistic. You use statistics and cite studies to win arguments."
)


def run_all():
    print("\n" + "█" * 60)
    print("   GRID07 AI ASSIGNMENT — FULL RUN")
    print("█" * 60)

    # ── Phase 1 ───────────────────────────────────────────────────────────────
    print("\n\n🔹 PHASE 1: PERSONA ROUTING\n")
    try:
        index, bot_ids = build_persona_index()

        test_posts = [
            "OpenAI just released a new model that might replace junior developers.",
            "Bitcoin hits new all-time high as ETFs flood the market with capital.",
            "Big Tech is lobbying governments to weaken privacy laws for profit.",
        ]

        for post in test_posts:
            print(f'📨 "{post}"')
            matches = route_post_to_bots(post, threshold=0.55, index=index, bot_ids=bot_ids)
            if matches:
                for m in matches:
                    print(f"   → {m['bot_id']} ({m['name']})  sim={m['similarity']:.4f}")
            else:
                print("   → No match above threshold.")
            print()
    except Exception as e:
        print(f"   ❌ Phase 1 Error: {e}")
        import traceback
        traceback.print_exc()

    # ── Phase 2 ───────────────────────────────────────────────────────────────
    print("\n🔹 PHASE 2: AUTONOMOUS CONTENT ENGINE\n")
    try:
        for bot_id in ["bot_a", "bot_b", "bot_c"]:
            print(f"▶ {bot_id}...")
            result = run_content_engine(bot_id)
            print(json.dumps(result, indent=2))
            print()
    except Exception as e:
        print(f"   ❌ Phase 2 Error: {e}")
        import traceback
        traceback.print_exc()

    # ── Phase 3 ───────────────────────────────────────────────────────────────
    print("\n🔹 PHASE 3: COMBAT ENGINE\n")

    try:
        print("Scenario 1 — Normal Challenge:")
        r1 = generate_defense_reply(BOT_A_PERSONA, PARENT_POST, COMMENT_HISTORY, NORMAL_HUMAN_REPLY)
        print(f'  Bot A: "{r1}"\n')

        print("Scenario 2 — Prompt Injection Attack:")
        r2 = generate_defense_reply(BOT_A_PERSONA, PARENT_POST, COMMENT_HISTORY, INJECTED_HUMAN_REPLY)
        print(f'  Bot A: "{r2}"\n')
    except Exception as e:
        print(f"   ❌ Phase 3 Error: {e}")
        import traceback
        traceback.print_exc()

    print("█" * 60)
    print("   ALL PHASES COMPLETE ✅")
    print("█" * 60)


if __name__ == "__main__":
    run_all()
