"""Code-verified numeric items for india-hr-bench.
Answers are computed, never written by hand. Standard library only.
Rules encoded (VERIFY against official text before release; see README):
  - wage base = max(basic + DA + retaining, 50% of total remuneration)
  - gratuity  = last drawn monthly wage * 15 / 26 * completed years
"""
import json, random, sys

def wage_base(total_rem, basic_da):
    return max(basic_da, 0.5 * total_rem)

def gratuity(monthly_wage, years):
    return monthly_wage * 15 / 26 * years

def make_items(n=20, seed=7):
    rnd = random.Random(seed)
    items = []
    for i in range(n):
        total = rnd.choice(range(40_000, 300_001, 5_000))
        basic = rnd.choice(range(int(total * 0.2), int(total * 0.7), 1_000))
        base = wage_base(total, basic)
        items.append({
            "id": f"NUM-WAGE-{i:03d}", "track": "labour_codes", "answer_type": "numeric",
            "prompt": (f"An Indian employer pays total monthly remuneration of Rs {total:,}. "
                       f"Basic + DA is Rs {basic:,}; the rest is allowances. Under the Code on Wages "
                       f"(in force since 21 Nov 2025), what monthly amount is the wage base for PF/gratuity "
                       f"purposes? Answer with a number in rupees."),
            "expected": round(base), "generator": "wage_base", "as_of": "2026-10-26",
            "review_status": "needs_review"})
    for i in range(n):
        wage = rnd.choice(range(20_000, 200_001, 2_500))
        yrs = rnd.randint(5, 20)
        items.append({
            "id": f"NUM-GRAT-{i:03d}", "track": "labour_codes", "answer_type": "numeric",
            "prompt": (f"Last drawn monthly wage is Rs {wage:,}. Completed continuous service is {yrs} years. "
                       f"Using the standard gratuity formula (15/26 x wage x years), compute gratuity in rupees, "
                       f"rounded to the nearest rupee."),
            "expected": round(gratuity(wage, yrs)), "generator": "gratuity", "as_of": "2026-10-26",
            "review_status": "needs_review"})
    return items

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    for it in make_items(n):
        print(json.dumps(it, ensure_ascii=False))
