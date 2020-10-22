SELECT
    t."datetime",
    t."id_tweet",
    t."tweet_body",
    t."source",
    t."id_user",
    t."name_user",
    t."id_recipient",
    t."name_recipient",
    t."geo"[1] "latitude",
    t."geo"[2] "longitude",
    "name_place",
    "country",
    "retweeted",
    hshtg."hashtag",
    COALESCE(
        hshtg."flg_ny",
        CASE
            WHEN LOWER(t."tweet_body") LIKE '%new%year%'
            THEN TRUE
            ELSE NULL
        END
    ) "flg_ny"
FROM
    twitter.ny2020 t
LEFT JOIN
    (
        SELECT
            base."datetime",
            base."id_tweet",
            base."hashtag",
            flg."flg_ny"
        FROM
            (
                SELECT
                    "datetime",
                    "id_tweet",
                    UNNEST("hashtags") "hashtag"
                FROM
                    twitter.ny2020
            ) base
        LEFT JOIN
            (
                SELECT
                    "datetime",
                    "id_tweet",
                    TRUE "flg_ny"
                FROM
                    (
                        SELECT
                            "datetime",
                            "id_tweet",
                            UNNEST("hashtags") "hashtag"
                        FROM
                            twitter.ny2020
                    ) foo
                WHERE
                    LOWER("hashtag") LIKE '%new%year%'
                GROUP BY
                    1, 2
            ) flg
            ON
            base."datetime" = flg."datetime"
            AND
            base."id_tweet" = flg."id_tweet"
    ) hshtg
    ON
    t."datetime" = hshtg."datetime"
    AND
    t."id_tweet" = hshtg."id_tweet"