import pandas as pd

# Load your full research data
person1 = pd.read_csv(r"C:\Users\Mihir\Downloads\Person 1-Grid view.csv")
person2 = pd.read_csv(r"C:\Users\Mihir\Downloads\Person 2-Grid view.csv")
matched = pd.read_csv(r"C:\Users\Mihir\Downloads\similar_notes_output.csv")

# Add consistent identifiers
person1['Person'] = 'Analyst 1'
person2['Person'] = 'Analyst 2'

person1['Sr. No.'] = pd.to_numeric(person1['Sr. No.'], errors='coerce')
person2['Sr. No.'] = pd.to_numeric(person2['Sr. No.'], errors='coerce')
matched['Person 1 Sr. No.'] = pd.to_numeric(matched['Person 1 Sr. No.'], errors='coerce')
matched['Person 2 Sr. No.'] = pd.to_numeric(matched['Person 2 Sr. No.'], errors='coerce')

# Drop rows where Sr. No. is missing
person1 = person1.dropna(subset=['Sr. No.'])
person2 = person2.dropna(subset=['Sr. No.'])
matched = matched.dropna(subset=['Person 1 Sr. No.', 'Person 2 Sr. No.'])

# Convert to int (now safe)
person1['Sr. No.'] = person1['Sr. No.'].astype(int)
person2['Sr. No.'] = person2['Sr. No.'].astype(int)
matched['Person 1 Sr. No.'] = matched['Person 1 Sr. No.'].astype(int)
matched['Person 2 Sr. No.'] = matched['Person 2 Sr. No.'].astype(int)


# Add unique key
person1['Key'] = 'P1_' + person1['Sr. No.'].astype(str)
person2['Key'] = 'P2_' + person2['Sr. No.'].astype(str)
matched['Key1'] = 'P1_' + matched['Person 1 Sr. No.'].astype(str)
matched['Key2'] = 'P2_' + matched['Person 2 Sr. No.'].astype(str)

# === Step 4: Assign Cluster IDs to Matches ===
clustered = []
cluster_id = 1

for _, row in matched.iterrows():
    clustered.append({'Key': row['Key1'], 'Cluster ID': cluster_id})
    clustered.append({'Key': row['Key2'], 'Cluster ID': cluster_id})
    cluster_id += 1

cluster_df = pd.DataFrame(clustered)

# === Step 5: Combine All Notes ===
combined = pd.concat([person1, person2], ignore_index=True)
combined['Key'] = combined['Key'].astype(str)

# Ensure cluster map uses unique keys
cluster_map = cluster_df.drop_duplicates(subset='Key').set_index('Key')['Cluster ID']
combined['Cluster ID'] = combined['Key'].map(cluster_map)

# Assign new Cluster ID to unmatched notes
next_cluster_id = cluster_df['Cluster ID'].max() + 1 if not cluster_df.empty else 1
unmatched_mask = combined['Cluster ID'].isna()
new_ids = range(next_cluster_id, next_cluster_id + unmatched_mask.sum())
combined.loc[unmatched_mask, 'Cluster ID'] = list(new_ids)

# Final formatting
combined['Cluster ID'] = combined['Cluster ID'].astype(int)
combined['Is Matched'] = combined.duplicated(subset='Cluster ID', keep=False)


# Export fixed consolidated CSV
combined.to_csv("consolidated_notes.csv", index=False)
print("✅ Fixed consolidated_notes.csv created.")
