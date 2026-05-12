type BrandMarkProps = {
  className?: string;
};

export default function BrandMark({ className = 'h-12 w-12' }: BrandMarkProps) {
  return (
    <img
      src="./icon-128x128.png"
      alt=""
      aria-hidden="true"
      draggable={false}
      className={className}
    />
  );
}
