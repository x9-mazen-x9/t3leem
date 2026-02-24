import logoBlack from "../assets/images/MAJMA-logo/black-majma.png";
import logoWhite from "../assets/images/MAJMA-logo/white-majma.png";
import logoFullBlack from "../assets/images/MAJMA-logo/MAGMA-dis-black.png";
import logoFullWhite from "../assets/images/MAJMA-logo/MAGMA-dis-white.png";

const Logo = ({ variant = "icon", isDark = false, className = "" }) => {
  let src;

  if (variant === "full") {
    src = isDark ? logoFullWhite : logoFullBlack;
  } else {
    src = isDark ? logoWhite : logoBlack;
  }

  return <img src={src} alt="MAJMA Logo" className={className} />;
};

export default Logo;