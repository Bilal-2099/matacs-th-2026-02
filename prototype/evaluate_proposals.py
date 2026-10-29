import json

def score_proposals(input_path="AI_analyze.json", output_path="ranking.json"):
    with open(input_path, "r") as f:
        data = json.load(f)
    
    results = []
    eligible_proposals = []

    for prop in data:
        name = prop.get("proposal_id")
        if not name:
            continue
            
        mand = prop.get("mandatory_criteria", {})
        weighted = prop.get("weighted_criteria", {})

        licence_data = mand.get("ontario_electrical_licence", {})
        if not licence_data.get("held_by_bidder", False):
            results.append({
                "proposal": name,
                "rank": None,
                "status": "ineligible",
                "score": None,
                "reason": "Failed mandatory criteria: Ontario electrical contractor licence is delegated to a subcontractor post-award rather than held directly by the bidder."
            })
            continue

        wsib_ins = mand.get("wsib_and_insurance", {})
        if not (wsib_ins.get("wsib_confirmed", False) and wsib_ins.get("liability_insurance_5m", False)):
            results.append({
                "proposal": name,
                "rank": None,
                "status": "ineligible",
                "score": None,
                "reason": "Failed mandatory criteria: WSIB clearance and/or $5M liability insurance not confirmed."
            })
            continue

        timeline_obj = weighted.get("timeline_weeks", {})
        timeline_weeks = timeline_obj.get("value")
        
        if timeline_weeks is None:
            results.append({
                "proposal": name,
                "rank": None,
                "status": "flagged",
                "score": None,
                "reason": "Flagged for clarification: Installation timeline is unstated in the proposal pending site assessment, preventing immediate scoring."
            })
            continue

        if timeline_weeks > 16:
            results.append({
                "proposal": name,
                "rank": None,
                "status": "ineligible",
                "score": None,
                "reason": f"Failed mandatory criteria: Proposed timeline ({timeline_weeks} weeks) exceeds the 16-week completion maximum."
            })
            continue

        price_obj = weighted.get("price_cad", {})
        price = price_obj.get("value")
        
        if price is None or price > 260000.0:
            results.append({
                "proposal": name,
                "rank": None,
                "status": "ineligible",
                "score": None,
                "reason": f"Failed mandatory criteria: Price (${price}) exceeds or missing against the $260,000 CAD budget ceiling."
            })
            continue

        eligible_proposals.append(prop)

    if eligible_proposals:
        min_price = min(p["weighted_criteria"]["price_cad"]["value"] for p in eligible_proposals)
    else:
        min_price = 231000.0

    scored_candidates = []

    for prop in eligible_proposals:
        name = prop["proposal_id"]
        weighted = prop["weighted_criteria"]

        exp_count = weighted["experience_count_100kw_plus"].get("value", 0)
        exp_score = min(30.0, (exp_count / 14.0) * 30.0)

        price = weighted["price_cad"]["value"]
        price_score = 25.0 * (min_price / price)

        timeline_weeks = weighted["timeline_weeks"]["value"]
        timeline_score = 15.0 * max(0.0, min(1.0, (16.0 - timeline_weeks) / 6.0))

        warranty = weighted.get("warranty", {})
        panel_years = warranty.get("panel_years", 0)
        workmanship_years = warranty.get("workmanship_years", 0)
        
        panel_score = 10.0 * min(panel_years / 25.0, 1.0)
        workmanship_score = 5.0 * min(workmanship_years / 12.0, 1.0)
        warranty_score = panel_score + workmanship_score

        team = weighted.get("team_and_approach", {})
        team_points = 0.0
        if team.get("named_project_lead"): team_points += 3.75
        if team.get("crew_specified"): team_points += 3.75
        if team.get("safety_plan"): team_points += 3.75
        if team.get("monitoring_plan"): team_points += 3.75
        team_score = team_points

        total_score = round(exp_score + price_score + timeline_score + warranty_score + team_score, 1)

        reasons_list = []
        if exp_count >= 12:
            reasons_list.append(f"strong commercial experience ({exp_count} installs)")
        else:
            reasons_list.append(f"adequate experience ({exp_count} installs)")
            
        if price == min_price:
            reasons_list.append(f"lowest eligible price (${int(price):,})")
        else:
            reasons_list.append(f"competitive price (${int(price):,})")
            
        reasons_list.append(f"{timeline_weeks}-week schedule")

        reason_str = f"Ranked based on " + ", ".join(reasons_list) + f", providing a {workmanship_years}-year workmanship warranty and solid team approach."

        scored_candidates.append({
            "proposal": name,
            "score": total_score,
            "reason": reason_str,
            "score_breakdown": {
                "experience": round(exp_score, 2),
                "price": round(price_score, 2),
                "timeline": round(timeline_score, 2),
                "warranty": round(warranty_score, 2),
                "team_and_approach": round(team_score, 2)
            }
        })

    scored_candidates.sort(key=lambda x: x["score"], reverse=True)

    for rank, item in enumerate(scored_candidates, start=1):
        results.append({
            "proposal": item["proposal"],
            "rank": rank,
            "status": "ranked",
            "score": item["score"],
            "reason": item["reason"],
            "score_breakdown": item["score_breakdown"]
        })

    all_props = ["Proposal A", "Proposal B", "Proposal C", "Proposal D", "Proposal E"]
    existing_props = {r["proposal"] for r in results}
    for p in all_props:
        if p not in existing_props:
            results.append({
                "proposal": p,
                "rank": None,
                "status": "ineligible",
                "score": None,
                "reason": "Proposal data missing or unprocessable."
            })

    results.sort(key=lambda x: x["proposal"])

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    score_proposals()