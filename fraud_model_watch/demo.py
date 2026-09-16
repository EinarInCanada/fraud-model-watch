"""Small standard-library-only demonstration of delayed aggregate feedback."""
import argparse
import json

from .stress import deterministic_scenarios, simulate


def run():
    scenarios = deterministic_scenarios()
    rows = []
    for name in ('stable', 'abrupt', 'recovery', 'sparse'):
        series = scenarios[name]
        result = simulate(series)
        rows.append(dict(scenario=name,
            observations=[dict(event_month=e.month, labels_available_at=e.month + 2,
                               positives=e.positives, captured=e.captured) for e in series],
            **result))
    return dict(provenance='hand-specified aggregate counts, not BAF or real bank incidents',
        rule='two mature consecutive months, >=30 positives each, >=5pp recall drop, two-month cooldown',
        timing='event-month m labels arrive at m+2; a request does not execute or prove useful retraining',
        scenarios=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true', help='show all event/label/decision traces')
    args = parser.parse_args()
    result = run()
    if args.json:
        print(json.dumps(result, indent=2))
        return
    print('FRAUD MODEL WATCH | COUNT-BASED DEMO')
    print(result['provenance'])
    print(result['timing'])
    print('\nScenario    Request decisions   Interpretation')
    notes = {'stable': 'No observed decline.', 'abrupt': 'Change starts at event 5; first request is decision 8.',
             'recovery': 'Recovery starts at event 7, but stale feedback still requests at decision 8.',
             'sparse': 'Too few positive labels; silence is not evidence of health.'}
    for row in result['scenarios']:
        print(f"{row['scenario']:<11} {str(row['requests']):<19} {notes[row['scenario']]}")
    print('\nUse --json for complete traces. See docs/RESEARCH_REPORT.md for measured results and limits.')


if __name__ == '__main__':
    main()
