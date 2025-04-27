import os
import h5py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Directory where all reconstructions are saved
base_dir = "./recon_tests/"

# Initialize list to collect results
results = []

# Loop through all reconstruction subfolders
for folder in sorted(os.listdir(base_dir)):
    folder_path = os.path.join(base_dir, folder)
    if not os.path.isdir(folder_path):
        continue

    # Find the latest H5 file inside this folder
    h5_files = [f for f in os.listdir(folder_path) if f.endswith(".h5")]
    if not h5_files:
        continue
    h5_files.sort()
    latest_h5 = os.path.join(folder_path, h5_files[-1])

    try:
        with h5py.File(latest_h5, "r") as f:
            # Try to access photon error history
            if "runtime/errors" in f:
                photon_errors = f["runtime/errors/photon"][:]
                final_photon_error = photon_errors[-1] if len(photon_errors) > 0 else np.nan
            else:
                final_photon_error = np.nan

        # Save the result
        results.append({
            "Folder": folder,
            "Final Photon Error": final_photon_error
        })

    except Exception as e:
        print(f"Warning: Failed to read {latest_h5} because {e}")

# Turn into DataFrame
df = pd.DataFrame(results)

# Sort by lowest photon error first
df_sorted = df.sort_values(by="Final Photon Error", ascending=True)

# Save to CSV
csv_path = "recon_summary.csv"
df_sorted.to_csv(csv_path, index=False)
print(f"✅ CSV summary saved to {csv_path}")

# Print top 5
print("\n🔵 Top 5 reconstructions by photon error:")
print(df_sorted.head(5))

# Plot the best reconstruction
if len(df_sorted) > 0:
    best_folder = df_sorted.iloc[0]["Folder"]
    best_folder_path = os.path.join(base_dir, best_folder)

    h5_files = [f for f in os.listdir(best_folder_path) if f.endswith(".h5")]
    h5_files.sort()
    best_h5 = os.path.join(best_folder_path, h5_files[-1])

    with h5py.File(best_h5, "r") as f:
        object_data = f["recons/obj/Sscan_00G00/mean"][:]
        amplitude = np.abs(object_data[0])
        phase = np.angle(object_data[0])

    # Plot amplitude and phase
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.imshow(amplitude, cmap="gray")
    ax1.set_title("Amplitude (Best Reconstruction)")
    plt.colorbar(ax1.images[0], ax=ax1)

    ax2.imshow(phase, cmap="twilight_shifted")
    ax2.set_title("Phase (Best Reconstruction)")
    plt.colorbar(ax2.images[0], ax=ax2)

    plt.tight_layout()
    plt.show()
