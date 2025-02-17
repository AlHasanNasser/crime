import api from "../api";
import Nav from "../components/Nav";
import Footer from "../components/footer";
import img from "../assets/crime/1.png";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
const NewsPage = () => {
  const [news, setNews] = useState([]);
  const { newsId } = useParams();
  useEffect(() => {
    // Fetch all news
    api
      .get(`/api/notes/${newsId}/`)
      .then((response) => {
        setNews(response.data); // Set the news data
      })
      .catch((error) => {
        console.error("Error fetching the news:", error);
      });

    // Fetch saved news
  }, [newsId]);
  if (!news) {
    return <div>Loading...</div>; // Display loading state while fetching data
  }
  return (
    <div>
      <Nav />
      <div className="newspage-container">
        <div className="newspage-content">
          {news.image && (
            <img src={img} alt={news.title} className="newspage-image" />
          )}
          <h1 className="newspage-title">{news.title}</h1>
          <p className="newspage-body">{news.body}</p>
          <p className="newspage-date">
            {new Date(news.created).toLocaleDateString()}
          </p>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default NewsPage;
