html = '''
<head>
<style>
	html {{
 
}}

*,
*:before,
*:after {{
    box-sizing: inherit;
}}

body {{
    margin: 0;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}}

.container {{
    position: relative;
    width: 900px;
    height: 600px;
    border: 2px solid white;
}}

.container .img {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-size: 900px 100%;
}}

.container .background-img {{
    background-image: url({color});
}}

.container .foreground-img {{
    background-image: url({bw});
    width: 50%;
}}

.container .slider {{
    position: absolute;
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    height: 100%;
    background: rgba(242, 242, 242, 0.3);
    outline: none;
    margin: 0;
    transition: all 0.2s;
    display: flex;
    justify-content: center;
    align-items: center;
}}

.container .slider:hover {{
    background: rgba(242, 242, 242, 0.1);
}}

.container .slider::-webkit-slider-thumb {{
    -webkit-appearance: none;
    appearance: none;
    width: 6px;
    height: 600px;
    background: white;
    cursor: pointer;
}}

.container .slider::-moz-range-thumb {{
    width: 6px;
    height: 600px;
    background: white;
    cursor: pointer;
}}

.container .slider-button {{
    pointer-events: none;
    position: absolute;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background-color: white;
    left: calc(50% - 18px);
    top: calc(50% - 18px);
    display: flex;
    justify-content: center;
    align-items: center;
}}

.container .slider-button:after {{
    content: "";
    padding: 3px;
    display: inline-block;
    border: solid #5d5d5d;
    border-width: 0 2px 2px 0;
    transform: rotate(-45deg);
}}

.container .slider-button:before {{
    content: "";
    padding: 3px;
    display: inline-block;
    border: solid #5d5d5d;
    border-width: 0 2px 2px 0;
    transform: rotate(135deg);
}}
</style>
<script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
</head>

<body>
 <div class='container'>
    <div class='img background-img'></div>
    <div class='img foreground-img'></div>
    <input type="range" min="1" max="100" value="50" class="slider" name='slider' id="slider">
    <div class='slider-button'></div>

  <script>
   $("#slider").on("input change", (e)=>{{
	const sliderPos = e.target.value;
	// Update the width of the foreground image
	$('.foreground-img').css('width', `${{sliderPos}}%`)
	// Update the position of the slider button
	$('.slider-button').css('left', `calc(${{sliderPos}}% - 18px)`)
	}});

  </script>
  

  </div>


</body>
	'''