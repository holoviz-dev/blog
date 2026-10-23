SELECT
  "NAME",
  "POP_EST",
  "geometry"
FROM countries
WHERE
  NOT "POP_EST" IS NULL