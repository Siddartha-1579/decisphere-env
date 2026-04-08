import logo from '@/assets/logo.png';

export default function Header() {
  return (
    <header className="flex items-center gap-3 px-8 py-5">
      <img src={logo} alt="DeciSphere AI" className="h-10 w-10" />
      <h1 className="font-display text-2xl font-bold tracking-tight text-foreground">
        DeciSphere AI
      </h1>
    </header>
  );
}
