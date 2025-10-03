import React from "react";
import "../../styles/globals.css";

export const metadata = {
  title: "Requirements",
  description: "Requirement pages built from PASS components",
};

const RequirementsReqLayout = ({ children }: { children: React.ReactNode }) => {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  );
};

export default RequirementsReqLayout;
