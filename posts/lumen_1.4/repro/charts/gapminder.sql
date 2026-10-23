WITH top10 AS (
  SELECT
    "country"
  FROM data_gapminder_json
  WHERE
    "year" = 2005
  ORDER BY
    "pop" DESC
  LIMIT 10
)
SELECT
  g."country",
  g."year",
  g."fertility",
  g."life_expect",
  g."pop"
FROM data_gapminder_json AS g
JOIN top10 AS t
  ON g."country" = t."country"
WHERE
  g."year" BETWEEN 1955 AND 2005
ORDER BY
  g."country",
  g."year"