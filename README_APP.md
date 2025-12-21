# Twilight Zone Episode Explorer

A beautiful, interactive Streamlit dashboard for exploring La Quatrième Dimension (The Twilight Zone) episode data scraped from French Wikipedia.

## Features

- **📊 Dashboard**: Statistics, charts, and visualizations
  - Episodes per season bar chart
  - Season distribution pie chart
  - Data completeness metrics
  - Season breakdown table

- **📺 Episode Browser**: Browse all 156 episodes
  - Table or card view
  - Filter by season
  - Search by title
  - Sort by season/episode or title
  - Click episodes to view details

- **🔍 Search**: Real-time search across all episodes
  - Search titles (French and English)
  - Filter by multiple seasons simultaneously
  - See results instantly

- **✨ Beautiful UI**: Twilight Zone themed design
  - Dark purple/black color scheme
  - Vintage TV aesthetic
  - Responsive layout
  - Interactive charts

## Installation

1. Ensure Python 3.8+ is installed

2. Install dependencies:
```bash
cd F:/DEV/SRC/TWILIGHT_ZONE
pip install -r requirements_app.txt
```

This will install:
- Streamlit (dashboard framework)
- Pandas (data manipulation)
- Plotly (interactive charts)

## Usage

### Running the App

Simply run:
```bash
streamlit run app.py
```

The app will automatically open in your default browser at `http://localhost:8501`

### Navigation

1. **Sidebar**: Use the navigation to switch between Dashboard and Episodes pages
2. **Filters**:
   - Select seasons to display (default: all seasons)
   - Enter search terms to filter episodes
3. **Dashboard**: View statistics and charts about the entire series
4. **Episodes**: Browse, search, and view detailed episode information

### Features in Detail

#### Dashboard Page
- See overall statistics (total seasons, episodes, averages)
- View interactive charts showing episode distribution
- Check data completeness percentage
- See season-by-season breakdown

#### Episode Browser
- **Table View**: Sortable table with all episodes
  - Click any row to see full episode details below
- **Card View**: Expandable cards for each episode
- **Sorting**: By season/episode or alphabetically by title
- **Filtering**: Use sidebar to filter by season and search

#### Episode Details
Each episode shows:
- French and English titles
- Season and episode numbers
- Director and writer (when available)
- Air dates for USA and France
- Production code
- Full synopsis

## Data Source

The app uses `output/twilight_zone_episodes.json` which contains:
- 5 seasons of The Twilight Zone
- 156 total episodes
- Episode metadata from French Wikipedia

To regenerate the data, run the scraper:
```bash
python main.py
```

## Customization

### Changing Themes
Edit the CSS in `app.py` under the `st.markdown` section to customize colors and styling.

### Adding Features
The app is organized into modular functions:
- `load_data()` - Data loading and caching
- `render_dashboard()` - Dashboard page
- `render_episode_browser()` - Episode browser page
- `render_episode_details()` - Episode detail view
- Chart creation functions for visualizations

## Troubleshooting

### Port Already in Use
If port 8501 is in use, Streamlit will automatically try the next available port. You can also specify a different port:
```bash
streamlit run app.py --server.port 8502
```

### Data File Not Found
Ensure `output/twilight_zone_episodes.json` exists. Run the scraper if needed:
```bash
python main.py
```

### Dependencies Not Installing
Try upgrading pip first:
```bash
python -m pip install --upgrade pip
pip install -r requirements_app.txt
```

## Performance

- **Load Time**: <2 seconds
- **Data Caching**: Enabled with `@st.cache_data`
- **Responsive**: Handles all 156 episodes smoothly
- **Interactive**: Real-time search and filtering

## Tech Stack

- **Streamlit**: Web app framework (pure Python, no HTML/CSS/JS needed)
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive charts and visualizations
- **Python 3.8+**: Core language

## Screenshots

### Dashboard
The dashboard shows:
- Total statistics cards
- Interactive bar chart of episodes per season
- Pie chart showing season distribution
- Detailed season breakdown table

### Episode Browser
- Filterable table view of all episodes
- Search functionality across titles
- Season multiselect filter
- Click-to-view episode details

## Project Structure

```
F:/DEV/SRC/TWILIGHT_ZONE/
├── app.py                          # Main Streamlit application (single file)
├── requirements_app.txt            # Python dependencies
├── output/
│   └── twilight_zone_episodes.json # Episode data
├── README_APP.md                   # This file
└── README.md                       # Scraper documentation
```

## Development

To modify the app:

1. Edit `app.py` with your changes
2. Save the file
3. Streamlit will auto-reload in the browser
4. No need to restart manually!

### Adding New Pages
Add a new function and include it in the navigation:
```python
def render_new_page(df):
    st.header("New Page")
    # Your content here

# In main():
page = st.sidebar.radio("Navigate", ["Dashboard", "Episodes", "New Page"])
if page == "New Page":
    render_new_page(df)
```

### Adding New Charts
Use Plotly Express for quick charts:
```python
import plotly.express as px

fig = px.bar(data, x='column1', y='column2', title='My Chart')
st.plotly_chart(fig, use_container_width=True)
```

## License

This project is for educational purposes. Episode data sourced from French Wikipedia.

## Credits

- Built with Streamlit
- Data from French Wikipedia (fr.wikipedia.org)
- Visualization powered by Plotly
- Created with Claude Code

## Future Enhancements

Potential additions:
- Export episodes to CSV
- Favorite episodes feature
- Advanced filtering (by director, writer, year)
- Timeline visualization
- Episode comparison tool
- Dark/light theme toggle
- Mobile-responsive design improvements

## Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Ensure all dependencies are installed
3. Verify the data file exists
4. Check Python version (3.8+ required)

Enjoy exploring The Twilight Zone! 🌌
