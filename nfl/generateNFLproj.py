import pandas as pd
import sys
import re
import time

starttime = time.time()

fpath = "C:\\Users\\brose32\\Downloads\\" + sys.argv[2]

df = pd.read_csv(fpath, usecols=["Id", "Nickname", "Position", "Salary", "Game", "Team", "Opponent", "Injury Indicator"])
df = df[(df["Injury Indicator"] != "IR")]
df = df.drop(columns=["Injury Indicator"])
qbs_fd_df = df[(df["Position"] == "QB")].reset_index(drop=True)
dst_fd_df = df[(df["Position"] == "D")].reset_index(drop=True)
rbs_fd_df = df[(df["Position"] == "RB")].reset_index(drop=True)
wrs_fd_df = df[(df["Position"] == "WR")].reset_index(drop=True)
tes_fd_df = df[(df["Position"] == "TE")].reset_index(drop=True)
statsfpath = "C:\\Users\\brose32\\Documents\\" + sys.argv[1]
offense_stats_df = pd.read_excel(statsfpath, sheet_name="OFF STATS")
defense_rating_df = pd.read_excel(statsfpath, sheet_name="DEF RAT")
vegas_df = pd.read_excel(statsfpath, sheet_name="VEGAS LINES")
snaps_df = pd.read_excel(statsfpath, sheet_name="TEAMSNAPs")
qb_stats_df = pd.read_excel(statsfpath, sheet_name="QB STATS")
rb_stats_df = pd.read_excel(statsfpath, sheet_name="RB STATS")
wr_stats_df = pd.read_excel(statsfpath, sheet_name="WR STATS")
te_stats_df = pd.read_excel(statsfpath, sheet_name="TE STATS")
qb_snaps_df = pd.read_excel(statsfpath, sheet_name="QB SNAPS")
rb_snaps_df = pd.read_excel(statsfpath, sheet_name="RB SNAPS")
wr_snaps_df = pd.read_excel(statsfpath, sheet_name="WR SNAPS")
te_snaps_df = pd.read_excel(statsfpath, sheet_name="TE SNAPS")
team_play_type_df = pd.read_excel(statsfpath, sheet_name="TEAMRush%")
team_ppg_df = pd.read_excel(statsfpath, sheet_name="TEAMPPG")

x = re.search('.+?(?= \()', qb_stats_df.loc[3, "NAME"])

for i in range(len(qbs_fd_df)):
    qbs_fd_df.loc[i, "Team Snaps"] = (snaps_df[(snaps_df["Team Name"] == qbs_fd_df.loc[i, "Team"])]["Snaps/g"].values[0] \
                                        + defense_rating_df[(defense_rating_df["TEAM"] == qbs_fd_df.loc[i, "Opponent"])]["Opp Plays"].values[0]) / 2
    snap_per = qb_snaps_df[(qb_snaps_df["NAME"] == qbs_fd_df.loc[i, "Nickname"])]["SNAP%"]
    if len(snap_per) > 0:
        qbs_fd_df.loc[i, "Snap pct"] = snap_per.values[0]
        qbs_fd_df.loc[i, "Rush%"] = qb_snaps_df[(qb_snaps_df["NAME"] == qbs_fd_df.loc[i, "Nickname"])]["RUSH%"].values[0]
    else:
        qbs_fd_df.loc[i, "Snap pct"] = 0
        qbs_fd_df.loc[i, "Rush%"] = 0
    qbs_fd_df.loc[i, "Pass%"] = team_play_type_df[(team_play_type_df["Team Name"] == qbs_fd_df.loc[i,"Team"])]["Pass%"].values[0]

    stats = qb_stats_df[(qb_stats_df["NAME"] == qbs_fd_df.loc[i,"Nickname"])]
    qbs_fd_df.loc[i, "Team PPG"] = team_ppg_df[(team_ppg_df["Team Name"]) == qbs_fd_df.loc[i, "Team"]]["PPG"].values[0]
    qbs_fd_df.loc[i, "Imp"] = vegas_df[vegas_df["TEAM"] == qbs_fd_df.loc[i, "Team"]]["Imp"].values[0]

    if len(stats) > 0:

        qbs_fd_df.loc[i, 'Yds/a'] = stats.values[0][1]
        qbs_fd_df.loc[i, 'PaTd/per'] = stats.values[0][2]
        qbs_fd_df.loc[i, 'Yd/r'] = stats.values[0][4]
        qbs_fd_df.loc[i, 'Td/r'] = stats.values[0][5]
        qbs_fd_df.loc[i, 'Int/a'] = stats.values[0][3]
    else:
        qbs_fd_df.loc[i, "Yds/a"] = 0
        qbs_fd_df.loc[i, 'PaTd/per'] = 0
        qbs_fd_df.loc[i, 'Yd/r'] = 0
        qbs_fd_df.loc[i, 'Td/r'] = 0
        qbs_fd_df.loc[i, 'Int/a'] = 0
    qbs_fd_df.loc[i, "OPD"] = defense_rating_df[(defense_rating_df["TEAM"] == qbs_fd_df.loc[i, "Opponent"])]["Y/Pa"].values[0]
    qbs_fd_df.loc[i, "ORD"] = defense_rating_df[(defense_rating_df["TEAM"] == qbs_fd_df.loc[i, "Opponent"])]["RuYd/A"].values[0]
    snap_proj = qbs_fd_df.loc[i, "Team Snaps"] * qbs_fd_df.loc[i,"Snap pct"]
    qbs_fd_df.loc[i, "FD PROJ"] = (snap_proj * qbs_fd_df.loc[i, "Pass%"] * qbs_fd_df.loc[i, "Yds/a"] * qbs_fd_df.loc[i, "OPD"] * .04) + \
                                  (snap_proj * qbs_fd_df.loc[i, "Pass%"] * qbs_fd_df.loc[i, "PaTd/per"] * qbs_fd_df.loc[i, "OPD"] * 4) - \
                                  (snap_proj * qbs_fd_df.loc[i, "Pass%"] * qbs_fd_df.loc[i, "Int/a"] *  (1 + (1-qbs_fd_df.loc[i, "OPD"]))) + \
                                  (snap_proj * (1-qbs_fd_df.loc[i,"Pass%"])* qbs_fd_df.loc[i, "Rush%"] * qbs_fd_df.loc[i, "Yd/r"] * qbs_fd_df.loc[i,"ORD"]* 0.1) + \
                                  (snap_proj * (1 - qbs_fd_df.loc[i, "Pass%"]) * qbs_fd_df.loc[i, "Rush%"] * qbs_fd_df.loc[i, "Td/r"] * qbs_fd_df.loc[i, "ORD"] * 6) * \
                                  (qbs_fd_df.loc[i, "Imp"] / qbs_fd_df.loc[i, "Team PPG"])

for i in range(len(rbs_fd_df)):
    rbs_fd_df.loc[i, "Team Snaps"] = (snaps_df[(snaps_df["Team Name"] == rbs_fd_df.loc[i, "Team"])]["Snaps/g"].values[0] \
                                      + defense_rating_df[(defense_rating_df["TEAM"] == rbs_fd_df.loc[i, "Opponent"])][
                                          "Opp Plays"].values[0]) / 2
    snap_per = rb_snaps_df[(rb_snaps_df["NAME"] == rbs_fd_df.loc[i, "Nickname"])]["SNAP%"]
    if len(snap_per) > 0:
        rbs_fd_df.loc[i, "Snap pct"] = snap_per.values[0]
        rbs_fd_df.loc[i, "Rush%"] = rb_snaps_df[(rb_snaps_df["NAME"] == rbs_fd_df.loc[i, "Nickname"])]["RUSH%"].values[
            0]
        rbs_fd_df.loc[i, "Target%"] = rb_snaps_df[(rb_snaps_df["NAME"] == rbs_fd_df.loc[i, "Nickname"])]["TARGET%"].values[
            0]
    else:
        rbs_fd_df.loc[i, "Snap pct"] = 0
        rbs_fd_df.loc[i, "Rush%"] = 0
        rbs_fd_df.loc[i, "Target%"] = 0
    team_rush = team_play_type_df[(team_play_type_df["Team Name"] == rbs_fd_df.loc[i, "Team"])]["Rush%"].values[0]
    stats = rb_stats_df[(rb_stats_df["NAME"] == rbs_fd_df.loc[i, "Nickname"])]
    if len(stats) > 0:
        rbs_fd_df.loc[i, 'Yd/r'] = stats.values[0][1]
        rbs_fd_df.loc[i, 'RuTd/r'] = stats.values[0][2]
        rbs_fd_df.loc[i, 'Catch%'] = stats.values[0][3]
        rbs_fd_df.loc[i, 'Yd/c'] = stats.values[0][4]
        rbs_fd_df.loc[i, 'Td/c'] = stats.values[0][5]
    else:
        rbs_fd_df.loc[i, 'Yd/r'] = 0
        rbs_fd_df.loc[i, 'RuTd/r'] = 0
        rbs_fd_df.loc[i, 'Catch%'] = 0
        rbs_fd_df.loc[i, 'Yd/c'] = 0
        rbs_fd_df.loc[i, 'Td/c'] = 0
    rbs_fd_df.loc[i, "Team PPG"] = team_ppg_df[(team_ppg_df["Team Name"]) == rbs_fd_df.loc[i, "Team"]]["PPG"].values[0]
    rbs_fd_df.loc[i, "Imp"] = vegas_df[vegas_df["TEAM"] == rbs_fd_df.loc[i, "Team"]]["Imp"].values[0]
    rbs_fd_df.loc[i, "OPD"] = \
    defense_rating_df[(defense_rating_df["TEAM"] == rbs_fd_df.loc[i, "Opponent"])]["Y/Pa"].values[0]
    rbs_fd_df.loc[i, "ORD"] = \
    defense_rating_df[(defense_rating_df["TEAM"] == rbs_fd_df.loc[i, "Opponent"])]["RuYd/A"].values[0]
    snap_proj = rbs_fd_df.loc[i, "Team Snaps"] * rbs_fd_df.loc[i, "Snap pct"]
    rbs_fd_df.loc[i, "FD PROJ"] = (snap_proj * rbs_fd_df.loc[i, "Rush%"] * rbs_fd_df.loc[i, "Yd/r"] * 0.1 * rbs_fd_df.loc[i, "ORD"]) + \
                                  (snap_proj * rbs_fd_df.loc[i, "Rush%"] * rbs_fd_df.loc[i, 'RuTd/r'] * 6 * rbs_fd_df.loc[i, "ORD"]) + \
                                  (snap_proj * rbs_fd_df.loc[i, "Target%"] * rbs_fd_df.loc[i, 'Catch%'] * 0.5 * rbs_fd_df.loc[i, "OPD"]) + \
                                  (snap_proj * rbs_fd_df.loc[i, "Target%"] * rbs_fd_df.loc[i, 'Catch%'] * rbs_fd_df.loc[i, 'Yd/c'] * 0.1 * rbs_fd_df.loc[i, "OPD"]) + \
                                  (snap_proj * rbs_fd_df.loc[i, "Target%"] * rbs_fd_df.loc[i, 'Catch%'] * rbs_fd_df.loc[i, 'Td/c'] * 6 * rbs_fd_df.loc[i, "OPD"]) * \
                                  (rbs_fd_df.loc[i, "Imp"] / rbs_fd_df.loc[i, "Team PPG"])
for i in range(len(wrs_fd_df)):
    wrs_fd_df.loc[i, "Team Snaps"] = (snaps_df[(snaps_df["Team Name"] == wrs_fd_df.loc[i, "Team"])]["Snaps/g"].values[0] \
                                      + defense_rating_df[(defense_rating_df["TEAM"] == wrs_fd_df.loc[i, "Opponent"])][
                                          "Opp Plays"].values[0]) / 2
    snap_per = wr_snaps_df[(wr_snaps_df["NAME"] == wrs_fd_df.loc[i, "Nickname"])]["SNAP%"]
    if len(snap_per) > 0:
        wrs_fd_df.loc[i, "Snap pct"] = snap_per.values[0]
        wrs_fd_df.loc[i, "Rush%"] = wr_snaps_df[(wr_snaps_df["NAME"] == wrs_fd_df.loc[i, "Nickname"])]["RUSH%"].values[
            0]
        wrs_fd_df.loc[i, "Target%"] = \
        wr_snaps_df[(wr_snaps_df["NAME"] == wrs_fd_df.loc[i, "Nickname"])]["TARGET%"].values[
            0]
    else:
        wrs_fd_df.loc[i, "Snap pct"] = 0
        wrs_fd_df.loc[i, "Rush%"] = 0
        wrs_fd_df.loc[i, "Target%"] = 0
    team_rush = team_play_type_df[(team_play_type_df["Team Name"] == wrs_fd_df.loc[i, "Team"])]["Rush%"].values[0]
    stats = wr_stats_df[(wr_stats_df["NAME"] == wrs_fd_df.loc[i, "Nickname"])]
    if len(stats) > 0:
        wrs_fd_df.loc[i, 'Yd/r'] = stats.values[0][1]
        wrs_fd_df.loc[i, 'RuTd/r'] = stats.values[0][2]
        wrs_fd_df.loc[i, 'Catch%'] = stats.values[0][3]
        wrs_fd_df.loc[i, 'Yd/c'] = stats.values[0][4]
        wrs_fd_df.loc[i, 'Td/c'] = stats.values[0][5]
    else:
        wrs_fd_df.loc[i, 'Yd/r'] = 0
        wrs_fd_df.loc[i, 'RuTd/r'] = 0
        wrs_fd_df.loc[i, 'Catch%'] = 0
        wrs_fd_df.loc[i, 'Yd/c'] = 0
        wrs_fd_df.loc[i, 'Td/c'] = 0
    wrs_fd_df.loc[i, "Team PPG"] = team_ppg_df[(team_ppg_df["Team Name"]) == wrs_fd_df.loc[i, "Team"]]["PPG"].values[0]
    wrs_fd_df.loc[i, "Imp"] = vegas_df[vegas_df["TEAM"] == wrs_fd_df.loc[i, "Team"]]["Imp"].values[0]
    wrs_fd_df.loc[i, "OPD"] = \
        defense_rating_df[(defense_rating_df["TEAM"] == wrs_fd_df.loc[i, "Opponent"])]["Y/Pa"].values[0]
    wrs_fd_df.loc[i, "ORD"] = \
        defense_rating_df[(defense_rating_df["TEAM"] == wrs_fd_df.loc[i, "Opponent"])]["RuYd/A"].values[0]
    snap_proj = wrs_fd_df.loc[i, "Team Snaps"] * wrs_fd_df.loc[i, "Snap pct"]
    wrs_fd_df.loc[i, "FD PROJ"] = (snap_proj * wrs_fd_df.loc[i, "Rush%"] * wrs_fd_df.loc[i, "Yd/r"] * 0.1 *
                                   wrs_fd_df.loc[i, "ORD"]) + \
                                  (snap_proj * wrs_fd_df.loc[i, "Rush%"] * wrs_fd_df.loc[i, 'RuTd/r'] * 6 *
                                   wrs_fd_df.loc[i, "ORD"]) + \
                                  (snap_proj * wrs_fd_df.loc[i, "Target%"] * wrs_fd_df.loc[i, 'Catch%'] * 0.5 *
                                   wrs_fd_df.loc[i, "OPD"]) + \
                                  (snap_proj * wrs_fd_df.loc[i, "Target%"] * wrs_fd_df.loc[i, 'Catch%'] * wrs_fd_df.loc[
                                      i, 'Yd/c'] * 0.1 * wrs_fd_df.loc[i, "OPD"]) + \
                                  (snap_proj * wrs_fd_df.loc[i, "Target%"] * wrs_fd_df.loc[i, 'Catch%'] * wrs_fd_df.loc[
                                      i, 'Td/c'] * 6 * wrs_fd_df.loc[i, "OPD"]) * (wrs_fd_df.loc[i, "Imp"] / wrs_fd_df.loc[i, "Team PPG"])
#print(wrs_fd_df.head())
for i in range(len(tes_fd_df)):
    tes_fd_df.loc[i, "Team Snaps"] = (snaps_df[(snaps_df["Team Name"] == tes_fd_df.loc[i, "Team"])]["Snaps/g"].values[0] \
                                      + defense_rating_df[(defense_rating_df["TEAM"] == tes_fd_df.loc[i, "Opponent"])][
                                          "Opp Plays"].values[0]) / 2
    snap_per = te_snaps_df[(te_snaps_df["NAME"] == tes_fd_df.loc[i, "Nickname"])]["SNAP%"]

    if len(snap_per) > 0:
        tes_fd_df.loc[i, "Snap pct"] = snap_per.values[0]
        tes_fd_df.loc[i, "Rush%"] = te_snaps_df[(te_snaps_df["NAME"] == tes_fd_df.loc[i, "Nickname"])]["RUSH%"].values[
            0]
        tes_fd_df.loc[i, "Target%"] = \
            te_snaps_df[(te_snaps_df["NAME"] == tes_fd_df.loc[i, "Nickname"])]["TARGET%"].values[
                0]
    else:
        tes_fd_df.loc[i, "Snap pct"] = 0
        tes_fd_df.loc[i, "Rush%"] = 0
        tes_fd_df.loc[i, "Target%"] = 0
    team_rush = team_play_type_df[(team_play_type_df["Team Name"] == tes_fd_df.loc[i, "Team"])]["Rush%"].values[0]
    stats = te_stats_df[(te_stats_df["NAME"] == tes_fd_df.loc[i, "Nickname"])]
    if len(stats) > 0:
        tes_fd_df.loc[i, 'Catch%'] = stats.values[0][1]
        tes_fd_df.loc[i, 'Yd/c'] = stats.values[0][2]
        tes_fd_df.loc[i, 'Td/c'] = stats.values[0][3]
    else:
        tes_fd_df.loc[i, 'Catch%'] = 0
        tes_fd_df.loc[i, 'Yd/c'] = 0
        tes_fd_df.loc[i, 'Td/c'] = 0
    tes_fd_df.loc[i, "Team PPG"] = team_ppg_df[(team_ppg_df["Team Name"]) == tes_fd_df.loc[i, "Team"]]["PPG"].values[0]
    tes_fd_df.loc[i, "Imp"] = vegas_df[vegas_df["TEAM"] == tes_fd_df.loc[i, "Team"]]["Imp"].values[0]
    tes_fd_df.loc[i, "OPD"] = \
        defense_rating_df[(defense_rating_df["TEAM"] == tes_fd_df.loc[i, "Opponent"])]["Y/Pa"].values[0]
    tes_fd_df.loc[i, "ORD"] = \
        defense_rating_df[(defense_rating_df["TEAM"] == tes_fd_df.loc[i, "Opponent"])]["RuYd/A"].values[0]
    snap_proj = tes_fd_df.loc[i, "Team Snaps"] * tes_fd_df.loc[i, "Snap pct"]
    tes_fd_df.loc[i, "FD PROJ"] = (snap_proj * tes_fd_df.loc[i, "Target%"] * tes_fd_df.loc[i, 'Catch%'] * 0.5 *
                                   tes_fd_df.loc[i, "OPD"]) + \
                                  (snap_proj * tes_fd_df.loc[i, "Target%"] * tes_fd_df.loc[i, 'Catch%'] * tes_fd_df.loc[
                                      i, 'Yd/c'] * 0.1 * tes_fd_df.loc[i, "OPD"]) + \
                                  (snap_proj * tes_fd_df.loc[i, "Target%"] * tes_fd_df.loc[i, 'Catch%'] * tes_fd_df.loc[
                                      i, 'Td/c'] * 6 * tes_fd_df.loc[i, "OPD"]) * (tes_fd_df.loc[i, "Imp"] / tes_fd_df.loc[i, "Team PPG"])

#print(tes_fd_df.head())

for i in range(len(dst_fd_df)):
    dst_fd_df.loc[i, "Opp Snaps"] = (defense_rating_df[(defense_rating_df["TEAM"] == dst_fd_df.loc[i, "Team"])]["Opp Plays"].values[0] \
                                      + snaps_df[(snaps_df["Team Name"] == dst_fd_df.loc[i, "Opponent"])][
                                          "Snaps/g"].values[0]) / 2
    dst_fd_df.loc[i, "Opp Pass"] = team_play_type_df[team_play_type_df["Team Name"] == dst_fd_df.loc[i, "Opponent"]]["Pass%"].values[0]
    dst_fd_df.loc[i, "Pts Allowed"] = vegas_df[(vegas_df["TEAM"] == dst_fd_df.loc[i, "Opponent"])]["Imp"].values[0]
    dst_fd_df.loc[i, "tSack"] = defense_rating_df[(defense_rating_df["TEAM"] == dst_fd_df.loc[i, "Team"])]["Sackperc"].values[0]
    dst_fd_df.loc[i, "oSack"] = offense_stats_df[(offense_stats_df["TEAM"] == dst_fd_df.loc[i, "Opponent"])]["Sackper"].values[0]
    dst_fd_df.loc[i, "tTO"] = defense_rating_df[(defense_rating_df["TEAM"] == dst_fd_df.loc[i, "Team"])]["TOperc"].values[0]
    dst_fd_df.loc[i, "oTO"] = offense_stats_df[(offense_stats_df["TEAM"] == dst_fd_df.loc[i, "Opponent"])]["TOper"].values[0]
    if dst_fd_df.loc[i, "Pts Allowed"] <= 20:
        pts_allowed = 1
    elif dst_fd_df.loc[i, "Pts Allowed"] >= 28:
        pts_allowed = -1
    else:
        pts_allowed = 0
    dst_fd_df.loc[i, "FD PROJ"] = (dst_fd_df.loc[i, "Opp Snaps"] * dst_fd_df.loc[i, "Opp Pass"]) * ((dst_fd_df.loc[i, "tSack"] + dst_fd_df.loc[i, "oSack"])/2) + \
                                  pts_allowed + (dst_fd_df.loc[i, "Opp Snaps"] * ((dst_fd_df.loc[i, "tTO"] + dst_fd_df.loc[i, "oTO"]) /2) * 2)


z = pd.concat([qbs_fd_df[["Nickname", "FD PROJ"]], rbs_fd_df[["Nickname", "FD PROJ"]], wrs_fd_df[["Nickname", "FD PROJ"]],
               tes_fd_df[["Nickname", "FD PROJ"]], dst_fd_df[["Nickname", "FD PROJ"]]])

x = qbs_fd_df[["Id","Nickname", "Position", "Salary", "Team", "Opponent", "FD PROJ"]]
y = x.append(rbs_fd_df[["Id", "Nickname", "Position", "Salary", "Team", "Opponent", "FD PROJ"]], ignore_index=True).append(wrs_fd_df[["Id","Nickname", "Position", "Salary", "Team", "Opponent", "FD PROJ"]], ignore_index=True)\
    .append(tes_fd_df[["Id", "Nickname", "Position", "Salary", "Team", "Opponent", "FD PROJ"]],ignore_index=True).append(dst_fd_df[["Id", "Nickname", "Position", "Salary", "Team", "Opponent", "FD PROJ"]],ignore_index=True)
for i in range(len(y)):
    y.loc[i, "Value"] = y.loc[i, "FD PROJ"] / (y.loc[i, "Salary"] / 1000)
y.to_csv("C:\\Users\\brose32\\Documents\\NFLFDproj.csv", index=False)

