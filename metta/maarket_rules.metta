;; Market analysis rules for BASIX IP-Marketplace
;; Using MeTTa symbolic AI for intelligent asset management

;; Asset valuation rules
(= (asset-value $asset-type $region $utility-features $creator-reputation)
   (let* (($base-value (base-asset-value $asset-type $region))
          ($utility-bonus (utility-value-bonus $utility-features))
          ($reputation-multiplier (reputation-factor $creator-reputation)))
     (* $base-value $utility-bonus $reputation-multiplier)))

;; Base asset values by type and region
(= (base-asset-value NFT Mumbai) 2.0)
(= (base-asset-value NFT Delhi) 1.8)
(= (base-asset-value NFT Bangalore) 2.2)
(= (base-asset-value Phygital Mumbai) 3.5)
(= (base-asset-value Phygital Delhi) 3.2)
(= (base-asset-value Digital Global) 1.5)
(= (base-asset-value RealWorldAsset $region) 5.0)

;; Utility feature bonuses
(= (utility-value-bonus (streaming_rights)) 1.2)
(= (utility-value-bonus (revenue_share)) 1.5)
(= (utility-value-bonus (exclusive_access)) 1.3)
(= (utility-value-bonus (commercial_license)) 1.4)
(= (utility-value-bonus ()) 1.0)

;; Reputation factors
(= (reputation-factor $score) 
   (if (> $score 80) 1.3
       (if (> $score 60) 1.1
           (if (> $score 40) 1.0 0.8))))

;; Market trend analysis
(= (market-trend $asset-type $period)
   (trend-direction (price-history $asset-type $period)))

;; Collaboration scoring
(= (collaboration-score $creators $ownership-distribution)
   (let* (($diversity-score (creator-diversity-score $creators))
          ($balance-score (ownership-balance-score $ownership-distribution)))
     (* $diversity-score $balance-score)))

;; Investment recommendations
(= (recommend-investment $user-profile $market-state)
   (filter (lambda $asset (> (expected-return $asset $user-profile) 0.15))
           (available-assets $market-state)))