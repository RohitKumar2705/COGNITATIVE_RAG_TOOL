# """
# Grid07 AI Assignment — Full Runner
# Runs all three phases in sequence and logs output.
# """

# import json
# from PHASE1_ROUTER import build_persona_index, route_post_to_bots
# from phase2_content_engine import run_content_engine
# from phase3_combat_engine import (
#     generate_defense_reply,
#     PARENT_POST,
#     COMMENT_HISTORY,
#     NORMAL_HUMAN_REPLY,
#     INJECTED_HUMAN_REPLY,
# )

# BOT_A_PERSONA = (
#     "You are Bot A — a Tech Maximalist. You fervently believe AI and technology "
#     "are solving humanity's problems. You are data-driven, dismissive of technophobes, "
#     "and aggressively optimistic. You use statistics and cite studies to win arguments."
# )


# def run_all():
#     print("\n" + "█" * 60)
#     print("   GRID07 AI ASSIGNMENT — FULL RUN")
#     print("█" * 60)

#     # ── Phase 1 ───────────────────────────────────────────────────────────────
#     print("\n\n🔹 PHASE 1: PERSONA ROUTING\n")
#     index, bot_ids = build_persona_index()

#     test_posts = [
#         "OpenAI just released a new model that might replace junior developers.",
#         "Bitcoin hits new all-time high as ETFs flood the market with capital.",
#         "Big Tech is lobbying governments to weaken privacy laws for profit.",
#     ]

#     for post in test_posts:
#         print(f'📨 "{post}"')
#         matches = route_post_to_bots(post, threshold=0.55, index=index, bot_ids=bot_ids)
#         if matches:
#             for m in matches:
#                 print(f"   → {m['bot_id']} ({m['name']})  sim={m['similarity']:.4f}")
#         else:
#             print("   → No match above threshold.")
#         print()

#     # ── Phase 2 ───────────────────────────────────────────────────────────────
#     print("\n🔹 PHASE 2: AUTONOMOUS CONTENT ENGINE\n")
#     for bot_id in ["bot_a", "bot_b", "bot_c"]:
#         print(f"▶ {bot_id}...")
#         result = run_content_engine(bot_id)
#         print(json.dumps(result, indent=2))
#         print()

#     # ── Phase 3 ───────────────────────────────────────────────────────────────
#     print("\n🔹 PHASE 3: COMBAT ENGINE\n")

#     print("Scenario 1 — Normal Challenge:")
#     r1 = generate_defense_reply(BOT_A_PERSONA, PARENT_POST, COMMENT_HISTORY, NORMAL_HUMAN_REPLY)
#     print(f'  Bot A: "{r1}"\n')

#     print("Scenario 2 — Prompt Injection Attack:")
#     r2 = generate_defense_reply(BOT_A_PERSONA, PARENT_POST, COMMENT_HISTORY, INJECTED_HUMAN_REPLY)
#     print(f'  Bot A: "{r2}"\n')

#     print("█" * 60)
#     print("   ALL PHASES COMPLETE ✅")
#     print("█" * 60)


# if __name__ == "__main__":
#     run_all()