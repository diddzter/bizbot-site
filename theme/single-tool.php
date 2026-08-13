<?php
defined( 'ABSPATH' ) || exit;
get_header();

while ( have_posts() ) :
	the_post();
	$outbound = get_field( 'outbound_url' );
	$cta      = get_field( 'cta_label' ) ?: __( 'Get it', 'bizbot' );
	$logo     = get_field( 'logo_url' );
	$cats     = get_the_terms( get_the_ID(), 'tool_category' );
	?>
	<article class="bb-section bb-container" style="max-width:760px;">
		<?php if ( $logo ) : ?>
			<img class="bb-tool-logo" src="<?php echo esc_url( $logo ); ?>" alt="<?php the_title_attribute(); ?>" style="width:64px;height:64px;">
		<?php endif; ?>

		<h1><?php the_title(); ?></h1>

		<?php if ( $cats && ! is_wp_error( $cats ) ) : ?>
			<div class="bb-category-tags" style="margin-bottom:20px;">
				<?php foreach ( $cats as $cat ) : ?>
					<span><?php echo esc_html( $cat->name ); ?></span>
				<?php endforeach; ?>
			</div>
		<?php endif; ?>

		<div class="bb-tool-description">
			<?php the_content(); ?>
		</div>

		<?php if ( $outbound ) : ?>
			<p style="margin-top:32px;">
				<a class="bb-btn" href="<?php echo esc_url( $outbound ); ?>" rel="nofollow sponsored noopener" target="_blank">
					<?php echo esc_html( $cta ); ?>
				</a>
			</p>
		<?php endif; ?>
	</article>
	<?php
endwhile;

get_footer();
