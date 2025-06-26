import { motion } from "framer-motion";

const data = [30, 50, 80, 40, 70];

const BarGraph3D = () => {
  return (
    <div className="w-[100px] h-[100px] flex items-end gap-2 p-4 bg-[#2c3445] rounded-lg">
      {data.map((value, index) => (
        <motion.div
          key={index}
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: `${value}%`, opacity: 1 }}
          transition={{ duration: 0.8, delay: index * 0.2 }}
          className="w-8 rounded-md relative"
          style={{
            background: `linear-gradient(180deg, #5a6486 0%, #454F68 50%, #2c3445 100%)`,
            boxShadow:
              "2px 2px 8px rgba(0, 0, 0, 0.5), inset -2px -2px 5px rgba(255, 255, 255, 0.1)",
          }}
        />
      ))}
    </div>
  );
};

export default BarGraph3D;
