import { useState, useEffect } from "react";
import api from "../api"; // Import Axios instance
import Nav from "../components/Nav";
import Footer from "../components/footer";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
const CrimeMap = () => {
  const [crimeData, setCrimeData] = useState([]); // Store fetched data
  const [page, setPage] = useState(1); // Pagination state
  const [loading, setLoading] = useState(true); // Loading state
  const [hasMore, setHasMore] = useState(true); // State to track if there’s more data

  // Fetch data from the API when component mounts or page changes
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true); // Set loading to true when fetching starts
      try {
        // Request crime data from the API
        const response = await api.get("/api/crimes/", {
          params: { page: page }, // Pass the page number as a query parameter
        });

        // Set crime data from the API response
        setCrimeData(response.data.results);
        // Check if there's a next page of data
        setHasMore(response.data.next !== null);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
      setLoading(false); // Set loading to false once fetching completes
    };

    fetchData(); // Call the fetch function
  }, [page]); // Re-run effect when page changes

  // Go to the next page
  const goToNextPage = () => {
    if (hasMore) {
      setPage((prevPage) => prevPage + 1); // Increment page number
    }
  };

  // Go to the previous page
  const goToPreviousPage = () => {
    if (page > 1) {
      setPage((prevPage) => prevPage - 1); // Decrement page number
    }
  };

  return (
    <div>
      <Nav />
      <div className="map">
        <MapContainer
          center={[41.998469223, -87.670736531]}
          zoom={12}
          style={{ height: "80vh", width: "90%" }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; <a href='http://osm.org/copyright'>OpenStreetMap</a> contributors"
          />
          {crimeData.map((crime, index) => (
            <Marker key={index} position={[crime.latitude, crime.longitude]}>
              <Popup>
                <strong>Community Area:</strong> {crime.community_area}
                <br />
                <strong>Date:</strong> {crime.date}
                <br />
                <strong>Crime Count:</strong> {crime.crime_count}
                <br />
                <strong>Crime Rate:</strong> {crime.crime_rate}
              </Popup>
            </Marker>
          ))}
        </MapContainer>

        {!hasMore && <p>No more data available.</p>}

        {loading && <p>Loading...</p>}
      </div>
      <div className="rate-buttons">
        <button onClick={goToPreviousPage} disabled={page <= 1}>
          Previous
        </button>
        <button onClick={goToNextPage} disabled={!hasMore}>
          Next
        </button>
      </div>
      <Footer />
    </div>
  );
};

export default CrimeMap;
