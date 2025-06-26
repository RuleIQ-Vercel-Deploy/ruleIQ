import { BorderBeam } from "../magicui/border-beam";

interface GridProps {
  text: string;
  name: string;
}

export default function Grid2({ text, name }: GridProps) {
  return (
    <div
      className="w-[350px] h-[200px] rounded-xl flex flex-col items-start gap-6 justify-center p-4 relative"
      style={{ background: "linear-gradient(to bottom, #000000, #1a1a1a)" }}
    >
      <BorderBeam
        duration={6}
        delay={3}
        size={200}
        className="from-transparent via-blue-500 to-transparent"
      />
      <BorderBeam
        duration={6}
        delay={3}
        size={200}
        className="from-transparent via-blue-500 to-transparent"
      />
      <p className="text-gray-200 text-sm font-light">{text}</p>
      <p className="text-start text-sm">{name}</p>
    </div>
  );
}
