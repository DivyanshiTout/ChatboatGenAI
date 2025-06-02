import "./loading.css";

const Loading = () => {
  return (
<main>
	<div className="origami" role="img" aria-label="An optical illusion of a seemingly hot pink square that actually has its corners folded inward, which reveal while folding out that the square is really orange with a hot pink back side. Then the sequence repeats with the square being blue with an orange back side, once again with a purple square and blue back, then hot pink with a purple back.">
		<div className="origami__square">
			<div className="origami__flap"></div>
			<div className="origami__flap"></div>
			<div className="origami__flap"></div>
			<div className="origami__flap"></div>
		</div>
	</div>
</main>
  );
};

export default Loading;
