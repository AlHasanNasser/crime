import logo from "../assets/crime/logo.png";
import { Link } from "react-router-dom";

const Footer = () => {
  return (
    <footer className="footer-section">
      <div className="footer-container">
        <div className="footer-left">
          <h2 className="footer-title">
            <img src={logo} alt="logo" className="site-footer-logo" /> Crime
          </h2>
          <p className="footer-text">
            Lorem ipsum dolor sit amet consectetur adipisicing elit. Nam
            voluptas quos maxime obcaecati beatae sunt laboriosam alias sed
            accusamus? Voluptate accusamus aliquid sit rerum dolor doloremque,
            porro excepturi libero possimus?
          </p>
          <div className="social-icons">
            <a href="#">
              <i className="fab fa-facebook-f"></i>
            </a>
            <a href="#">
              <i className="fab fa-twitter"></i>
            </a>
            <a href="#">
              <i className="fab fa-linkedin-in"></i>
            </a>
            <a href="#">
              <i className="fab fa-google-plus-g"></i>
            </a>
            <a href="#">
              <i className="fab fa-youtube"></i>
            </a>
          </div>
        </div>

        <div className="footer-middle">
          <h4>ADDITIONAL RESEARCH LINKS</h4>
          <ul>
            <Link to={"/profile"}>
              <li>MY PROFILE</li>
            </Link>{" "}
            <Link to={"/news"}>
              <li>CHECK NEWS</li>
            </Link>{" "}
            <Link to={"/saved-news"}>
              <li>YOUR SAVES</li>
            </Link>{" "}
            <Link to={"/rates"}>
              <li>CRIMES RATES</li>
            </Link>{" "}
            <Link to={"/history"}>
              <li>HISTORY</li>
            </Link>{" "}
          </ul>
        </div>
      </div>
      <div className="footer-bottom">
        <p>&copy; Copyright 2018, Crime | All Rights Reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;
