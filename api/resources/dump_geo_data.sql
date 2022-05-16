SELECT json_build_object('type', 'FeatureCollection',
                         'features', json_agg(st_asgeojson(b)::json)) AS geojson
FROM (SELECT boro.*,
             json_build_object('type', 'FeatureCollection',
                               'features', json_agg(st_asgeojson(n)::json)) AS nta2020s
      FROM (SELECT nta2020.*,
                   json_build_object('type', 'FeatureCollection',
                                     'features', json_agg(h.geojson)) AS h3s
            FROM (SELECT h3_nta2020.nta2020_id,
                         st_asgeojson(h3)::json AS geojson
                  FROM h3
                  JOIN h3_nta2020 ON h3.h3_index = h3_nta2020.h3_index) AS h
            JOIN nta2020 ON nta2020.id = h.nta2020_id
            GROUP BY nta2020.id) AS n
      JOIN boro ON n.boro_id = boro.id
      GROUP BY boro.id) AS b;
