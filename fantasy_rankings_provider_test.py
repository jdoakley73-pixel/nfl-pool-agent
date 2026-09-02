from fantasy_rankings_provider import emergency_rankings, parse_ranked_list_html, parse_rankings_html


def test_table_parser():
    html = """
    <table>
      <thead><tr><th>RK</th><th>Player Name</th><th>POS</th><th>BYE WEEK</th><th>ADP</th></tr></thead>
      <tbody>
        <tr><td>1</td><td>Jahmyr Gibbs (DET)</td><td>RB1</td><td>6</td><td>1.2</td></tr>
        <tr><td>2</td><td>Ja'Marr Chase (CIN)</td><td>WR1</td><td>6</td><td>2.8</td></tr>
      </tbody>
    </table>
    """
    players = parse_rankings_html(html)
    assert len(players) == 2
    assert players[0].name == "Jahmyr Gibbs"
    assert players[0].position == "RB"
    assert players[0].position_rank == 1


def test_list_parser():
    html = """
    <ul>
      <li>1. Jahmyr Gibbs RB-DET</li>
      <li>2. Ja'Marr Chase WR-CIN</li>
      <li>3. Brock Bowers TE-LV</li>
    </ul>
    """
    players = parse_ranked_list_html(html)
    assert [p.name for p in players] == ["Jahmyr Gibbs", "Ja'Marr Chase", "Brock Bowers"]
    assert [p.position for p in players] == ["RB", "WR", "TE"]


def test_emergency_board_never_empty():
    players = emergency_rankings()
    assert len(players) >= 40
    assert players[0].name == "Jahmyr Gibbs"


if __name__ == "__main__":
    test_table_parser()
    test_list_parser()
    test_emergency_board_never_empty()
    print("fantasy rankings provider tests passed")
