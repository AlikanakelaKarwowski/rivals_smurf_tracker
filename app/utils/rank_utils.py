
def get_valid_ranks(rank_value:int, RANK_MAP: dict[str,int], RANKS: list[str]) -> list[int]:
        valid_ranks: list[int] = []

        # If rank is in Bronze or Silver
        if RANK_MAP["Bronze 3"] <= rank_value <= RANK_MAP["Silver 1"]:
            valid_ranks.extend(range(0, 9))

        # If rank is in Gold
        elif RANK_MAP["Gold 3"] <= rank_value <= RANK_MAP["Gold 1"]:
            valid_ranks.extend(range(0, 9))
            valid_ranks.extend(range(rank_value + 1, rank_value + 4))

        # If rank is in Platinum, Diamond, or Grand Master
        elif RANK_MAP["Platinum 3"] <= rank_value <= RANK_MAP["Celestial 1"]:
            valid_ranks.extend(range(max(rank_value - 3, 0), min(rank_value + 4, len(RANKS))))

        return valid_ranks
