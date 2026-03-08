# Electric Vehicle Analytics Dashboard

This project is a complete data analytics system that analyzes Electric Vehicle (EV) data such as charging patterns, battery performance, and EV model efficiency using **real-world CSV datasets**.

The insights are visualized using natively embedded interactive **Plotly charts**. This project has been converted into a **Static Website**, which means it consists entirely of plain HTML, CSS, and JS files, and requires no backend server.

Because there are no external dependencies on services like Flask or Tableau Public, this repository is completely self-contained and ready to be deployed to **GitHub Pages**.

## Project Structure

- `data/`: Contains the four real-world CSV files (`EVIndia.csv`, `ElectricCarData_Clean.csv`, `electric_vehicle_charging_station_list.csv`, `Cheapestelectriccars-EVDatabase.csv`).
- `build_static_site.py`: The Python builder script that processes the data and generates the HTML pages.
- `index.html`, `charging.html`, `battery.html`, `models.html`: The generated static pages containing embedded Plotly JSON data.
- `css/` & `js/`: Static stylesheet and optional logic scripts.
- `requirements.txt`: Python dependencies needed *only* to build/update the JSON graphs (`pandas`, `plotly`, `jinja2`).

## Deployment to GitHub Pages

To make these dashboards accessible online to anyone via GitHub Pages:

1. Create a Repository on GitHub and push these files to it.
2. Go to your repository **Settings** > **Pages**.
3. Under "Build and deployment", select the `main` branch and the `/ (root)` folder.
4. Click Save. Within a few minutes, your site will be published at `https://<your-username>.github.io/<repository-name>/`.

## How to Update the Dashboards

If the underlying CSV data changes, you do not need to edit the HTML manually. Simply run the build script to regenerate the static files:

### 1. Set up the Environment

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment:

- **Windows:**
  ```bash
  venv\Scripts\activate
  ```
- **macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

### 2. Install Build Dependencies

```bash
pip install -r requirements.txt
```

### 3. Build the Site

Run the Generator script. It will process the CSVs and overwrite the `.html` files in the root folder with updated interactive Plotly graphs.

```bash
python build_static_site.py
```

Commit the newly changed HTML files and push them to GitHub. GitHub Pages will automatically update with the new charts.
