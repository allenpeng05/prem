import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score

# load in data from scrapers
matches = pd.read_csv("matches.csv", index_col=0)
standings = pd.read_csv("standings_2014_15_to_2023_24.csv")


# map missing team names
class MissingDict(dict):
    def __missing__(self, key):
        return key


map_values = {
    "Brighton and Hove Albion": "Brighton",
    "Manchester United": "Manchester Utd",
    "Newcastle United": "Newcastle Utd",
    "Tottenham Hotspur": "Tottenham",
    "West Ham United": "West Ham",
    "Wolverhampton Wanderers": "Wolves",
}
mapping = MissingDict(**map_values)
matches["team"] = matches["team"].map(mapping)

# calculate the previous season
matches["prev_season"] = matches["season"] - 1


# merge the two dfs
merged_df = matches.merge(
    standings.rename(columns={"season": "prev_season", "rank": "prev_rank"}),
    on=["prev_season", "team"],
    how="left",
)

# now merge for opp rank as well
merged_df = merged_df.merge(
    standings.rename(
        columns={"season": "prev_season", "team": "opponent", "rank": "opp_prev_rank"}
    ),
    on=["prev_season", "opponent"],
    how="left",
)

# convert ranks back to integers, replace NaN with 20
merged_df["promote"] = merged_df["prev_rank"].isnull().astype(int)
merged_df["prev_rank"] = merged_df["prev_rank"].fillna(-1).astype(int)
merged_df["prev_rank"] = merged_df["prev_rank"].replace(-1, 20)
merged_df["opp_prev_rank"] = merged_df["opp_prev_rank"].fillna(-1).astype(int)
merged_df["opp_prev_rank"] = merged_df["opp_prev_rank"].replace(-1, 20)

# clean up data for ML model, conversion to int, etc
merged_df["date"] = pd.to_datetime(merged_df["date"])
merged_df["venue_code"] = merged_df["venue"].astype("category").cat.codes
# matches["team_code"] = matches["team"].astype("category").cat.codes
merged_df["opp_code"] = merged_df["opponent"].astype("category").cat.codes
merged_df["hour"] = merged_df["time"].str.replace(":.*", "", regex=True).astype("int")
merged_df["day_code"] = merged_df["date"].dt.dayofweek

# W = 2, L = 1, D = 0
merged_df["target"] = merged_df["result"].astype("category").cat.codes

# rank difference
merged_df["rank_diff"] = merged_df["prev_rank"] - merged_df["opp_prev_rank"]

# Using RandomForestClassifier to pick up non-linierarities
# comment to self: 40 = ~52%, 200 = ~32%,
rf = RandomForestClassifier(n_estimators=40, min_samples_split=10, random_state=1)


# Calculate rolling averages of key stats
def rolling_averages(group, cols, new_cols):
    group = group.sort_values("date")
    rolling_stats = group[cols].rolling(window=5, min_periods=1, closed="left").mean()
    group[new_cols] = rolling_stats
    group = group.dropna(subset=new_cols)
    return group


# Columns to calculate rolling averages for
cols = ["gf", "ga", "sh", "sot", "dist", "fk", "pk", "pkatt"]
new_cols = [f"{c}_rolling" for c in cols]

# group df by team, applies rolling_averages() to each team, then removes group index
matches_rolling = merged_df.groupby("team", group_keys=False).apply(
    lambda x: rolling_averages(x, cols, new_cols), include_groups=False
)
matches_rolling.index = range(matches_rolling.shape[0])


# Model training and evaluation
def make_predictions(data, predictors):

    # Training data set and test data set
    train = data[data["date"] < "2024-01-01"]
    test = data[data["date"] > "2024-01-01"]

    # Fits the rf on the training set, predicts onthe test set
    rf.fit(train[predictors], train["target"])
    preds = rf.predict(test[predictors])

    # Combines results and predictions into new df to calculate precision
    combined = pd.DataFrame(
        dict(actual=test["target"], prediction=preds), index=test.index
    )

    # Evaluate precision
    precision = precision_score(test["target"], preds, average="macro")
    return combined, precision


# Old predictors + new rolling averages
predictors = ["venue_code", "opp_code", "hour", "day_code"] + new_cols
# predictors = ["venue_code", "opp_code", "hour", "day_code", "rank_diff", "promote"] + new_cols
combined, precision = make_predictions(matches_rolling, predictors)
print(f"Precision: {precision}")
