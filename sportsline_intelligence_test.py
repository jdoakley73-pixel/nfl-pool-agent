from sportsline_intelligence import parse_sportsline_csv, summarize_signals


def test_parse_sportsline_csv_normalizes_confidence():
    signals = parse_sportsline_csv(
        "area,subject,recommendation,confidence,notes\n"
        "Survivor,LAC,Strong,82,Model likes matchup\n"
        "Pickem,KC vs DEN,KC,0.58,Close game\n"
    )
    assert len(signals) == 2
    assert signals[0].confidence == 0.82
    assert signals[1].confidence == 0.58


def test_parser_accepts_common_alias_columns():
    signals = parse_sportsline_csv("type,team,pick,confidence\nSurvivor,JAX,Use,70\n")
    assert signals[0].area == "Survivor"
    assert signals[0].subject == "JAX"
    assert signals[0].recommendation == "Use"


def test_summary_filters_area_and_orders_confidence():
    signals = parse_sportsline_csv(
        "area,subject,recommendation,confidence\n"
        "Fantasy,A,Start,60\nFantasy,B,Start,90\nSurvivor,LAC,Use,80\n"
    )
    summary = summarize_signals(signals, "Fantasy")
    assert summary["count"] == 2
    assert summary["high_confidence"][0]["subject"] == "B"
