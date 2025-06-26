interface GridProps {
  children: React.ReactNode;
  title: string;
  text: string;
}

export default function Grid({ children, title, text }: GridProps) {
  return (
    <div className="w-[350px] h-[300px] flex flex-col items-center gap-4 justify-center relative">
      <div className="absolute inset-x-0 top-[50px] z-0 flex justify-center">
        {/* Outer Soft Glow - Larger Ellipse */}
        <div
          className="absolute w-[300px] h-[200px] bg-[#5B698B]/40 opacity-80 blur-[80px]"
          style={{ borderRadius: "50%" }}
        />

        {/* Inner Glow - Smaller & Brighter Ellipse */}
        <div
          className="absolute w-[300px] h-[150px] bg-[#5B698B]/50 opacity-80 blur-[100px]"
          style={{ borderRadius: "50%" }}
        />
      </div>
      {/* Gradient Borders */}
      <div
        className="absolute top-0 left-[5%] w-[90%] h-[1px]"
        style={{
          background: "linear-gradient(to right, #0C0F16, #788DC5, #0C0F16)",
        }}
      ></div>
      <div
        className="absolute bottom-0 left-[5%] w-[90%] h-[1px]"
        style={{
          background: "linear-gradient(to right, #0C0F16, #788DC5, #0C0F16)",
        }}
      ></div>
      <div
        className="absolute left-0 top-[5%] h-[90%] w-[1px]"
        style={{
          background: "linear-gradient(to bottom, #0C0F16, #788DC5, #0C0F16)",
        }}
      ></div>
      <div
        className="absolute right-0 top-[5%] h-[90%] w-[1px]"
        style={{
          background: "linear-gradient(to bottom, #0C0F16, #788DC5, #0C0F16)",
        }}
      ></div>

      {/* White lines at center of each border */}
      <div className="absolute top-0 left-1/2 w-[30px] h-[2px] bg-white -translate-x-1/2"></div>
      <div className="absolute bottom-0 left-1/2 w-[30px] h-[2px] bg-white -translate-x-1/2"></div>
      <div className="absolute left-0 top-1/2 w-[2px] h-[30px] bg-white -translate-y-1/2"></div>
      <div className="absolute right-0 top-1/2 w-[2px] h-[30px] bg-white -translate-y-1/2"></div>

      {/* Pins on outer borders */}
      <div className="absolute top-[-8px] left-[-8px] w-[15px] h-[15px] bg-[#65749B] rounded-full flex items-center justify-center">
        <div className="w-[5px] h-[5px] bg-[#2C354A] rounded-full"></div>
      </div>
      <div className="absolute top-[-8px] right-[-8px] w-[15px] h-[15px] bg-[#65749B] rounded-full flex items-center justify-center">
        <div className="w-[5px] h-[5px] bg-[#2C354A] rounded-full"></div>
      </div>
      <div className="absolute bottom-[-8px] left-[-8px] w-[15px] h-[15px] bg-[#65749B] rounded-full flex items-center justify-center">
        <div className="w-[5px] h-[5px] bg-[#2C354A] rounded-full"></div>
      </div>
      <div className="absolute bottom-[-8px] right-[-8px] w-[15px] h-[15px] bg-[#65749B] rounded-full flex items-center justify-center">
        <div className="w-[5px] h-[5px] bg-[#2C354A] rounded-full"></div>
      </div>

      {/* Icon and Text */}
      {children}
      <p className="font-light text-[26px]">{title}</p>
      <p className="w-[90%] text-sm text-center font-light">{text}</p>
    </div>
  );
}
